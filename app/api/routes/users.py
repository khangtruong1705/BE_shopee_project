
from typing import Any
from app.api.routes.utils import verify_password,hash_password,create_access_token
from fastapi import APIRouter, Depends, HTTPException,status
from sqlmodel import Session, select
from app.models import Users, LoginData,RegisterData,ChangePasswordData,PayLoad
from app.core.db import engine,get_session
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter()





def send_email(to_email: str, user_name: str):
    # Thông tin Gmail (thay bằng thông tin của bạn)
    sender_email = "your_email@gmail.com"  # Thay bằng email của bạn
    sender_password = "your_app_password"  # Thay bằng App Password của Gmail

    # Tạo nội dung email
    subject = "Password Changed Successfully"
    body = f"""
    Dear {user_name},

    Your password has been successfully changed on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC.
    If you did not initiate this change, please contact our support team immediately.

    Best regards,
    Your Application Team
    """

    # Thiết lập email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Kết nối đến Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Bật TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")





def is_email_taken(session: Session, email: str) -> bool:
    statement = select(Users).where(Users.email == email)
    return session.exec(statement).first() is not None


@router.post("/register")
def register_user(register_data: RegisterData):
    with Session(engine) as session:
        # Kiểm tra xem email đã tồn tại chưa
        if is_email_taken(session, register_data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered !!!")

        # Băm mật khẩu
        hashed_password = hash_password(register_data.password)

        # Tạo đối tượng User mới
        new_user = Users(
            name=register_data.name,
            email=register_data.email,
            password=hashed_password,
            role="customer"  # Mặc định là customer
        )

        # Thêm vào cơ sở dữ liệu
        session.add(new_user)
        session.commit()

        return {"message": "User registered successfully !!!"}


@router.post("/login")
def login_user(login_data: LoginData):
    with Session(engine) as session:


        # Kiểm tra xem người dùng với email đã tồn tại chưa
        user = session.query(Users).filter(Users.email == login_data.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found !!!")

        # # Xác minh mật khẩu
        if not verify_password(login_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password !!!")

        # # Tạo token truy cập (access token)
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




@router.get("/get-user-by-user-id/{user_id}")
def get_user_by_id(user_id: int, session: Session = Depends(get_session)) -> Any:
    """
    API lấy thông tin user bằng user_id.
    """
    # Truy vấn để lấy user theo user_id
    statement = select(Users).where(Users.user_id == user_id)
    user = session.exec(statement).first()
    
    # Nếu không tìm thấy user, trả về lỗi
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    user_data = user.model_dump()  # Nếu sử dụng SQLModel, dict() sẽ có sẵn
    user_data.pop("password", None)  # Loại bỏ trường password nếu tồn tại
    return user_data

@router.post("/change-password")
def change_password(change_data: ChangePasswordData, session: Session = Depends(get_session)):
    try:
        # Kiểm tra xem người dùng với email đã tồn tại chưa
        statement = select(Users).where(Users.user_id == change_data.user_id)
        user =session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
        # # Xác minh mật khẩu cũ
        if not verify_password(change_data.old_password,user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password")
        if (change_data.new_password != change_data.confirm_new_password):
            raise HTTPException(status_code=400, detail=" Confirm-new-password Incorrect !")
        
        # Băm mật khẩu mới
        hashed_new_password = hash_password(change_data.new_password)

        # Cập nhật mật khẩu mới trong cơ sở dữ liệu
        user.password = hashed_new_password
        session.commit()

        # Gửi email thông báo
        # send_email(user.email, user.name)

        return {"message": "Password changed successfully and notification email sent"}

    except Exception as e:
        session.rollback()  # Rollback nếu có lỗi
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")

@router.put("/update-info-user-by-userid")
def update_info_user(payload:PayLoad,session: Session = Depends(get_session)
):
    # Lấy order item theo ID
    statement = select(Users).where(Users.user_id == payload.user_id)
    user =session.exec(statement).first()
    # Nếu không tồn tại thì trả về lỗi
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # # Cập nhật cột status 
    user.name = payload.data.name
    user.phone_number = payload.data.phone_number
    user.gender = payload.data.gender
    user.birthday = payload.data.birthday
   
    session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
      # Tải lại dữ liệu của order_item

    return {"message":"InfoUser changed successfully !!!"}   