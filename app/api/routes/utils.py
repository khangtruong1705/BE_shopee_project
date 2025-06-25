from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from datetime import datetime, timedelta,timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from fastapi import HTTPException
import os
import requests

# HASH PASSWORD
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# JSON WEB TOKEN
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")  
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data):
    to_encode = data.copy()
    to_encode.pop("password", None)

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Hợp lệ
    except jwt.ExpiredSignatureError:
        print("Token đã hết hạn")
        return None
    except jwt.InvalidTokenError:
        print("Token không hợp lệ")
        return None


# EMAIL
def send_email(sender_email,sender_password,to_email:str,subject,body):
    # Setting email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'html'))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Bật TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
def create_reset_password_token(email: str) -> str:
    if not isinstance(email, str):
        raise ValueError("Email must be a string")

    expire = datetime.now(timezone.utc) + timedelta(minutes=2)

    to_encode = {
        "sub": email,      
        "exp": expire,     
        "type": "reset"   
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_superset_access_token():
    url = "http://localhost:8088/api/v1/security/login"
    payload = {
        "username": "admin",   
        "password": "admin", 
        "provider": "db"
    }
    response = requests.post(url, json=payload)
    access_token = response.json()["access_token"]
    return access_token