from smtplib import *
from details import *
import requests
from bs4 import BeautifulSoup
from datetime import datetime, time, timedelta
from time import sleep
import os
import json
from decimal import Decimal
import re

START_TIME = time(6,0)
END_TIME = time(21,0)
FILENAME = "logs.json"
ERRNAME = "errors.json"
PRODUCT_URL = "https://www.amazon.in/Cubelelo-v3-Frosted-Speedcubing-Competition-Ready-Professionals/dp/B0FB8VSWYZ/ref=sr_1_6?crid=1GNOIPXRZX4YL&dib=eyJ2IjoiMSJ9.cOH8hvCnlIdyIZTYe68QRd4HgUI16rVP1Hkoraa2KFSmQO1o1If1_RGVKDCqfgf_NgI8qFPKHK_yKUHPuUP-4i_6NDSS6I_-u5-G0Z5To-gKKIMZ7VcnSjNW2c6qR-HT7sHgo3H0o8c3bhQb42bgjAbPlhF0sJ-Zt_yh52B8Q66DmhqY393DDLWiuyKGFIc8wubkLEk4IK2teeUBMeESK0r0EvKm2VZ_5waX1SN39tt88isp0l_b52ABHy8v4NtjWjV-K-DwQ4V7K2YxKF_hllOmSzxREqblp7fns1cgBP4.cPgjuES46WvWprvzJiQUulBtLq8DV1-GetMa1UbIwsw&dib_tag=se&keywords=rubik%27s+cube+gan&nsdOptOutParam=true&qid=1793883771&sprefix=rubik%27s+cube+ga%2Caps%2C352&sr=8-6"
TIMESPACE = 10

def send_email(to, From : str, password : str, subject : str, body : str, smtp_id : str = "smtp.gmail.com"):
    with SMTP(smtp_id, port=587) as connection:
        connection.starttls()
        connection.login(From, password)
        connection.sendmail(
            from_addr=From,
            to_addrs=to,
            msg=f"Subject: {subject}\n\n{body}"
        )

def add_to_json(key, value, name = FILENAME):
    # 1. Check if the file exists and is not empty
    now = datetime.now().time().strftime("%D-%H:%M:%S")

    if os.path.exists(name) and os.path.getsize(name) > 0:
        with open(name, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                os.makedirs("backups", exist_ok=True)
                backup_name = f"backups/{name}_{now}.corrupt"
                os.replace(name, backup_name)
                print(f"Invalid log moved to {backup_name}")
                data = {}
    else:
        # File doesn't exist or is empty, create a clean dictionary
        print(f"'{name}' not found. Creating a new one...")
        data = {}

    # 2. Add or update your data
    data[key] = value

    # 3. Save everything back to the file
    with open(name, "w") as file:
        json.dump(data, file, indent=4)
    
    print(f"Successfully saved '{key}:{value}' to {name}!")

    if name == ERRNAME:
        email_body = f"""
Dear User,

An error occured at {key}. You might want to stop or terminate the program
Error : {value}"""
        send_email(target, my_email, password, "ERROR", email_body)

def normalize_price(text):
    cleaned = re.sub(r"[^\d.,]", "", text)
    cleaned = cleaned.replace(",", "")
    return Decimal(cleaned)

def get_amazon_price(url):
    # Spoof a real browser session to avoid immediate blocks
    now = datetime.now().time().strftime("%D-%H:%M:%S")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://google.com"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Failed to retrieve page. Status code: {response.status_code}")
            return None
        if "captcha" in response.text.lower():
            print("Amazon returned a CAPTCHA page")
            add_to_json(now, "Amazon returned a CAPTCHA page", ERRNAME)
            return None
        if "robot check" in response.text.lower():
            print("Amazon returned a bot-check page")
            add_to_json(now, "Amazon returned a bot-check page", ERRNAME)
            return None
        # if "B0FTZ4GNRB" not in response.text:
        #     print("Unexpected Amazon page")
        #     add_to_json(now, "Unexpected Amazon page", ERRNAME)
        #     return None


        # Parse HTML text
        soup = BeautifulSoup(response.text, "html.parser")

        # Amazon regularly shifts HTML classes. We check the most common tags:
        price_whole = soup.find("span", class_="a-price-whole")
        price_fraction = soup.find("span", class_="a-price-fraction")
        
        if price_whole and price_fraction:
            # Reconstruct the price string (e.g., "24" + "." + "99")
            price = f"{price_whole.text.strip()}{price_fraction.text.strip()}"
            price = str(normalize_price(price))
            return price
        
        # Fallback check: hidden offscreen span sometimes holds the full string
        price_offscreen = soup.find("span", class_="a-offscreen")
        if price_offscreen:
            return str(normalize_price(price_offscreen.text.strip()))

        print("Could not find the price elements on the page.")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        add_to_json(now, str(e), ERRNAME)
        return None

def monitor():
    now = datetime.now()
    time_now = now.time()
    while True:
        now = datetime.now()
        time_now = now.time()
        while START_TIME <= time_now <= END_TIME:
            price = get_amazon_price(PRODUCT_URL)
            now = datetime.now()
            time_now = now.time()
            s_time_now = now.time().strftime("%D-%H:%M:%S")
            if price:
                add_to_json(s_time_now, price)
                print(f"Current Price: {price}")
            # else:
                # print("CAN'T ACCESS PRICE")
                # add_to_json(s_time_now, "ERROR: Cannot Access Price", ERRNAME)

            with open(FILENAME, "r") as file:
                curr_data = json.load(file)
            prices = [value for value in curr_data.values() if value != "ERROR: Cannot Access Price"]

            if price and len(prices) >= 2:
                previous_price = prices[-2]

                if previous_price != price:
                    email_body = f"""
    Dear User,

    The price at {PRODUCT_URL} changed from {previous_price} to {price}.
    """
                    send_email(target, my_email, password, "PRICE CHANGE", email_body)
                else:
                    print("No Change")
            elif not price:
                email_body = f"""
    Dear User,

    An error has occured, please check or stop the program
    This could be as the script could not access the price
    """
                send_email(target, my_email, password, "ERROR", email_body)

            sleep(TIMESPACE)
        print("No Send")
        sleep(TIMESPACE)

if __name__ == "__main__":
    monitor()