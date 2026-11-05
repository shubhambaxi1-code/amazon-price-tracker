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
TIMESPACE = 20
PRODUCT_URLS = [
    "https://www.amazon.in/Cubelelo-v3-Frosted-Speedcubing-Competition-Ready-Professionals/dp/B0FB8VSWYZ/ref=sr_1_6?crid=1GNOIPXRZX4YL&dib=eyJ2IjoiMSJ9.cOH8hvCnlIdyIZTYe68QRd4HgUI16rVP1Hkoraa2KFSmQO1o1If1_RGVKDCqfgf_NgI8qFPKHK_yKUHPuUP-4i_6NDSS6I_-u5-G0Z5To-gKKIMZ7VcnSjNW2c6qR-HT7sHgo3H0o8c3bhQb42bgjAbPlhF0sJ-Zt_yh52B8Q66DmhqY393DDLWiuyKGFIc8wubkLEk4IK2teeUBMeESK0r0EvKm2VZ_5waX1SN39tt88isp0l_b52ABHy8v4NtjWjV-K-DwQ4V7K2YxKF_hllOmSzxREqblp7fns1cgBP4.cPgjuES46WvWprvzJiQUulBtLq8DV1-GetMa1UbIwsw&dib_tag=se&keywords=rubik%27s+cube+gan&nsdOptOutParam=true&qid=1793883771&sprefix=rubik%27s+cube+ga%2Caps%2C352&sr=8-6", 
    "https://www.amazon.in/Lanterns-Diwali-Decoration-Colorful-Flying/dp/B0HL14LN6Y/ref=sr_1_8?crid=26WBR25YO2GUM&dib=eyJ2IjoiMSJ9.oWey3NYIKXkwK6OfoQcZbdZNgbMsHPTpFsZM_CSZhGli8VSWO_rpFI2pRXzCn4r14qp6YcmL9fcxYIW-U9HL9679lh2iKvmwIj5pija1Ij2UoZTZJbYq9RyALFDJa2xlOGhsAgvaq-lVVxtN2744go5cMkDOmY20en0ELgBJoOYjbDyWznxLZE52EbH5_X7eNTYaSFEcBBDVml89GLeAi3jVu5ev7dyzaV4vc3y6VWEYAkbcxTIXcKIVbpfqKs7olsN7OloKAHmShy6SaFUBk3bDV5cWiF2n3wKFaJbsqGM.9LOWXP-wrTdLwfKlHSvJD30u84_YRN9sBABim9v9tuI&dib_tag=se&keywords=crackers+for+diwali&qid=1793885383&sprefix=crac%2Caps%2C302&sr=8-8",
    "https://www.amazon.in/WOL3D-Bambu-Lab-A1-Printer/dp/B0DSLL17HD/ref=sr_1_1_sspa?crid=29FT675M7SWYS&dib=eyJ2IjoiMSJ9.rYUQla1aND6OmMvLwNxX_POfT2SwkkOIwJu7ewxrBTqa4Dv6pM9ovtWIRLd-F9n2FnkFX4maD3wwpsCusGkZehVdOgMCjoLnImSPS7DNiBJGp4zH-PTFer-K0NzbslNY-LqfJmd3a8FYsa3rZUTG6yI1Lq0FJRwKWWVmQ5hBYTofxaY-A-4j9stThiocP7wwPkRT8bR4vpw9jYpDOs6j1_FLAf1prwut1yFR0vBjsuVH1nU818BzRC2G3iqSY1z4KWPYVrita9-Bwu__T5ePyZ8yrp4YD1Sgkq7sm7f72Sg.8z_T1hdejdg-w4XNGvOUxM4m5tPN56OHvimI9m_OsOo&dib_tag=se&keywords=3d+printer&qid=1793888427&sprefix=3d+printe%2Caps%2C354&sr=8-1-spons&aref=FQqkHlGfHd&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1",
    "https://www.amazon.in/Logitech-K120-Wired-Keyboard-Black/dp/B006FEPRO4"
]

def send_email(to, From : str, password : str, subject : str, body : str, smtp_id : str = "smtp.gmail.com"):
    with SMTP(smtp_id, port=587) as connection:
        connection.starttls()
        connection.login(From, password)
        connection.sendmail(
            from_addr=From,
            to_addrs=to,
            msg=f"Subject: {subject}\n\n{body}"
        )

def add_to_json(key1, value, name = FILENAME, key2 = None,):
    # Load the existing history so each timestamp can hold multiple products.
    now = datetime.now().strftime("%d/%m/%Y-%H:%M")

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

    # Keep product prices nested below their shared timestamp.
    data.setdefault(key1, {})

    if not key2:
        data[key1] = value
    elif key2:
        data[key1][key2] = value

    # Rewrite the JSON file with the updated history.
    with open(name, "w") as file:
        json.dump(data, file, indent=4)
    
    print(f"Successfully saved '{value}' to {name}!")

    if name == ERRNAME:
        email_body = f"""
Dear User,

An error occured at {key1}/{key1}->{key2}. You might want to stop or terminate the program
Error : {value}"""
        send_email(target, my_email, password, "ERROR", email_body)

def normalize_price(text):
    # Store every scraped price in one comparable numeric format.
    cleaned = re.sub(r"[^\d.,]", "", text)
    cleaned = cleaned.replace(",", "")
    return Decimal(cleaned)

def get_amazon_price(url):
    # Use browser-like headers to reduce immediate blocking by Amazon.
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
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

        # Try the visible price parts first, then Amazon's off-screen fallback.
        soup = BeautifulSoup(response.text, "html.parser")

        price_whole = soup.find("span", class_="a-price-whole")
        price_fraction = soup.find("span", class_="a-price-fraction")
        
        if price_whole and price_fraction:
            price = f"{price_whole.text.strip()}{price_fraction.text.strip()}"
            price = str(normalize_price(price))
            return price
        
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
            # One timestamp groups all product prices from this monitoring cycle.
            s_time_now = now.strftime("%D-%H:%M:%S")
            for product in PRODUCT_URLS:
                price = get_amazon_price(product)
                now = datetime.now()
                if price:
                    add_to_json(s_time_now, price, key2=product)
                    print(f"Current Price: {price}")

                with open(FILENAME, "r") as file:
                    curr_data = json.load(file)

                # Compare this product only with its own previous prices.
                prices = [
                    entry[product]
                    for entry in curr_data.values()
                    if isinstance(entry, dict)
                    and product in entry
                    and entry[product] != "ERROR: Cannot Access Price"
                ]

                if price and len(prices) >= 2:
                    previous_price = prices[-2]

                    if previous_price != price:
                        email_body = f"""
Dear User,

The price at {product} changed from {previous_price} to {price}, by {round((float(price)/float(previous_price))*100, 2)}%
"""
                        print("PRICE CHANGE")
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
            # Wait until the next polling cycle after checking every product.
            for i in range(TIMESPACE):
                print(f"Waiting {i+1}/{TIMESPACE}")
                sleep(1)

        print("No Send")
        sleep(TIMESPACE)

if __name__ == "__main__":
    monitor()