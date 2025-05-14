from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




# Hàm để xác minh mật khẩu
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)



SECRET_KEY = "B3O6N9"
ALGORITHM = "HS256"  # Thuật toán mã hóa
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Thời gian tồn tại của token

# Hàm tạo access token
def create_access_token(data):
    to_encode = data.copy()
    to_encode.pop("password", None)

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt