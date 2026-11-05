from smtplib import *
from details import *

def send_email(to, From : str, password : str, subject : str, body : str, smtp_id : str = "smtp.gmail.com"):
    with SMTP(smtp_id, port=587) as connection:
        connection.starttls()
        connection.login(From, password)
        connection.sendmail(
            from_addr=From,
            to_addrs=to,
            msg=f"Subject: {subject}\n\n{body}"
        )

email = f"Test Email from {my_email} to {target}"

send_email(target, my_email, password, subject="Test Email", body=email)