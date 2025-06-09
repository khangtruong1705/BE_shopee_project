from typing import Any
from app.api.routes.utils import verify_password,hash_password,create_access_token,send_email,create_reset_password_token,decode_token
from fastapi import APIRouter, Depends, HTTPException,status,UploadFile, File,Form,Depends
from sqlmodel import Session, select
from app.models import Users, LoginData,RegisterData,ChangePasswordData,PayLoad,ForgotPasswordRequest,ResetPasswordRequest,Token,SMSRequest
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from app.core.db import get_session,engine
import os
import time
from datetime import datetime
import random
from google.oauth2 import id_token
from google.auth.transport import requests





router = APIRouter()


load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")



@router.post("/register")
def register_user(register_data: RegisterData):
      with Session(engine) as session:
        statement = select(Users).where(Users.email == register_data.email)
        existing_user = session.exec(statement).first()
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered !!!")
        hashed_password = hash_password(register_data.password)
        new_user = Users(
            name=register_data.name,
            email=register_data.email,
            password=hashed_password,
            role="customer"
        )
        session.add(new_user)
        session.commit()
        return {"detail": "User registered successfully !!!"}

@router.post("/login")
def login_user(login_data: LoginData,session: Session = Depends(get_session)):
        statement = select(Users).where(Users.email == login_data.email)
        user = session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found !!!")
        if not verify_password(login_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password !!!")
        token_data = {
          'user_id': user.user_id,
          'name':user.name,
          'email':user.email,
          'address':user.address,
          'phone_number':user.phone_number,
          'role':user.role
        }
        access_token = create_access_token(token_data)
        return access_token

@router.post("/auth/google")
async def google_login(token_request: Token,session: Session = Depends(get_session)):
    try:
        idinfo = id_token.verify_oauth2_token(
            token_request.token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        ) 
        statement = select(Users).where(Users.email == idinfo.get("email"))
        user = session.exec(statement).first()
        if not user:
            user = Users(
                name=idinfo.get("name"),
                email=idinfo.get("email"),
                password="",
                address=None,
                phone_number=None,
                role="user"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print("New user created:", user)  
        token_data = {
            'user_id': user.user_id,
            'name':user.name,
            'email':user.email,
            'address':user.address,
            'phone_number':user.phone_number,
            'role':user.role}
        access_token = create_access_token(token_data)
        return access_token

    except ValueError as e:
        # Token không hợp lệ
        print("ValueError:", e)
        raise HTTPException(status_code=400, detail="Invalid token")
    except Exception as e:
        # Lỗi khác
        print(f"Error verifying token: {e}")
        raise HTTPException(status_code=500, detail="Error verifying token")

@router.get("/get-user-by-user-id/{user_id}")
def get_user_by_id(user_id: int, session: Session = Depends(get_session)) -> Any:
    statement = select(Users).where(Users.user_id == user_id)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    user_data = user.model_dump()  
    user_data.pop("password", None)  
    return user_data

@router.post("/change-password")
def change_password(change_data: ChangePasswordData, session: Session = Depends(get_session)):
    try:
        statement = select(Users).where(Users.user_id == change_data.user_id)
        user =session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
        if not verify_password(change_data.old_password,user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password")
        if (change_data.new_password != change_data.confirm_new_password):
            raise HTTPException(status_code=400, detail=" Confirm-new-password Incorrect !")
        hashed_new_password = hash_password(change_data.new_password)
        user.password = hashed_new_password
        session.commit()
        # Send email Notification
        try:
            subject = "Password Changed Successfully"
            html_body = f"""
            <html>
            <body>
                <p>Dear You,</p>

                <p>
                Your password has been successfully changed on
                <strong>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</strong>.
                If you did not initiate this change, please contact our support team immediately.
                </p>

                <p>
                Best regards,<br>
                <em>Your Application Team</em>
                </p>
            </body>
            </html>
            """
            send_email(sender_email,sender_password,user.email,subject,html_body)
        except Exception as email_error:
              print(email_error)
        return {"detail": "Password changed successfully."}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")

@router.put("/update-info-user-by-userid")
def update_info_user(payload:PayLoad,session: Session = Depends(get_session)
):
    statement = select(Users).where(Users.user_id == payload.user_id)
    user =session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = payload.data.name
    user.phone_number = payload.data.phone_number
    user.gender = payload.data.gender
    user.birthday = payload.data.birthday
    session.commit()  
    return {"message":"InfoUser changed successfully !!!"}   


@router.post("/upload-avatar-by-userid")
async def upload_avatar(user_id: int = Form(...), avatar: UploadFile = File(...),session: Session = Depends(get_session)):
    statement = select(Users).where(Users.user_id == user_id)
    user =session.exec(statement).first()
    contents = await avatar.read()
    unix_timestamp = int(time.time())
    if not user.avatar_url:
        # Upload file to Cloudinary
            result = cloudinary.uploader.upload(
            contents,
            folder="avatars",
            public_id=f"{user_id}_{unix_timestamp}",  
            resource_type="image"
    )          
    if user.avatar_url :
        filename = user.avatar_url.rpartition('/')[2].split('.')[0]
        public_id = f"avatars/{filename}" 
        cloudinary.uploader.destroy(public_id, resource_type="image")
        result =  cloudinary.uploader.upload(
            contents,
            folder="avatars",
            public_id=f"{user_id}_{unix_timestamp}", 
            resource_type="image")
    user.avatar_url = result["secure_url"]
    session.commit()
    session.refresh(user)
    return {
        "avatar_url": result["secure_url"]
    }

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest,session: Session = Depends(get_session)):
    statement = select(Users).where(Users.email == data.email)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    token = create_reset_password_token(user.email)
    subject = "Password Reset Request"
    html_body = f"""
    <html>
        <body>
            <p>Your token to reset your password: <strong>{token}</strong></p>
        </body>
    </html>
    """
    try:
        send_email(sender_email,sender_password,user.email,subject,html_body)
    except Exception as email_error:
        print(email_error)
    user.reset_password_token = token
    session.commit()
    session.refresh(user)
    return user.email

@router.post("/check-reset-password-token")
async def check_reset_password_token(data:Token,session: Session = Depends(get_session)):
    statement = select(Users).where(Users.reset_password_token == data.token)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    return user.reset_password_token

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest,session: Session = Depends(get_session)):
    token = request.token
    decode_token(token)
    new_password = hash_password(request.new_password)
    statement = select(Users).where(Users.reset_password_token ==token) 
    user = session.exec(statement).first()
    user.password = new_password
    user.reset_password_token = None  
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Password reset successfully"}

access_token_speedsms=os.getenv("ACCESS_TOKEN_SPEEDSMS")
@router.post("/send-sms-otp")
def send_sms_otp(request: SMSRequest):
    otp = random.randint(100000, 999999)
    message = f"Mã OTP của bạn là: {otp}"

    url =   "https://api.speedsms.vn/index.php/sms/send"
           

    payload = {
        "to": request.phone_number,
        "content": message,
        "type": 2,  # 2 = OTP
    }

    headers = {
        "Access-Token": access_token_speedsms,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print("SpeedSMS response:", response.status_code, response.text)
        return {"status": "OK", "otp": otp, "api_response": response.json()}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}



