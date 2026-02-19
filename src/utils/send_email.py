import smtplib, random
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_verify_code(recipient_email):
	code = random.randint(100000, 999999)
	msg = EmailMessage()
	msg["Subject"] = "Verification"
	msg["From"] = EMAIL_ADDRESS
	msg["To"] = recipient_email
	msg.set_content(f"Your code is {code}")
	
	try:
		with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.send_message(msg)
		
		return {"ok": True, "msg": code}
	
	except Exception as e:
		return {"ok": False, "error": str(e)}
	
	


