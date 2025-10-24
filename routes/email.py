# from fastapi import Form, HTTPException, APIRouter, status
# from pydantic import EmailStr
# import smtplib
# from email.mime.text import MIMEText
# import os
# from db import application_forms_collection
# from dotenv import load_dotenv

# load_dotenv()

# email_router = APIRouter(tags=["Email"])

# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
# EMAIL_PORT= int(os.getenv("EMAIL_PORT"))
# EMAIL_HOST = os.getenv("EMAIL_HOST")
# PASSCODE = os.getenv("PASSCODE_REQUIRED")

# def send_email(recipient:str, body:str):
#     msg = MIMEText(body, "plain")
#     msg["From"] = EMAIL_USER
#     msg["To"] = recipient
#     msg["Subject"] = body

#     try:
#         with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
#             server.starttls()
#             server.login(EMAIL_USER, EMAIL_PASSWORD)
#             server.send_message(msg)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"{e}")


# @email_router.post("/send_passcode")
# def send_passcode(email: EmailStr = Form(...)):
#     # Check if user exists
#     form = application_forms_collection.find_one({"trainee_email": email})
#     if not form:
#         raise HTTPException(status_code=404, detail="Email not found in records")

#     # Send email with passcode
#     body = f"""
#     Congratulations, you've been selected for our program!
#     Your trainee passcode is: {PASSCODE}
#     Please enter this code to complete your registration.
    
#     Thank you,
#     Career Grooming Agency Team
#     """

#     send_email(email, body)
#     return {"message": f"Passcode sent successfully to {email}"}