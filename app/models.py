from datetime import datetime,date
from decimal import Decimal
from typing import Optional,List, Dict
from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from pydantic import BaseModel




class Products(SQLModel,table=True):
    __tablename__ = 'products'

    product_id: Optional[int] = Field(primary_key=True)
    name: str
    image: str
    description: Optional[str] = None
    price: float
    rating: Optional[float] = None  
    sold: Optional[int] = Field(default=0)  
    detailed_description: Optional[str] = None 
    category_id: Optional[int] = Field(default=None, foreign_key="categories.category_id", nullable=True)
    shop_name_id: Optional[int] = Field(default=None, foreign_key="shop_name.shop_name_id", nullable=True)
    created_at: Optional[date] = Field(default_factory=date.today)
    updated_at: Optional[date] = Field(default_factory=None)
    views:int = Field(default_factory=0)

class Users(SQLModel, table=True):
    __tablename__ = 'users'

    user_id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    address: str = None
    phone_number: str = None
    role: str = Field(default="customer")
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)
    gender:str
    birthday: date
    avatar_url : str
    reset_password_token:str

class Comments(SQLModel, table=True):
    __tablename__ = 'comments'

    comment_id: Optional[int] = Field(default=None, primary_key=True)
    comment_content: str = Field(...)
    user_id: Optional[int] = Field(default=None, foreign_key="users.user_id")
    product_id: Optional[int] = Field(default=None, foreign_key="products.product_id")
    created_at: Optional[date] = Field(default_factory=date.today)

class Categories(SQLModel, table=True):
    __tablename__ = 'categories'

    category_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str
    description: Optional[str] = None
    created_at: Optional[date] = Field(default_factory=date.today)
    updated_at: Optional[date] = Field(default=None)

class Carts(SQLModel, table=True):
    __tablename__ = "carts"

    cart_id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    user_id: Optional[int] = Field(default=None, foreign_key="users.user_id")
    status: Optional[str] = Field(default='pending', description="Order status")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp when the order was created")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp when the order was last updated")
    product_id: Optional[int] = Field(default=None, foreign_key="products.product_id")

class ShopName(SQLModel, table=True):
    __tablename__ = "shop_name"

    shop_name_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: Optional[str] = Field(default=None, nullable=True)
    rating: Optional[Decimal] = Field(default=None, nullable=True)
    created_at: Optional[date] = Field(default_factory=date.today, nullable=True)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.category_id", nullable=True)
    image:Optional[str]
    response_rate:int
    email_owner: Optional[str] = Field(default=None, foreign_key="users.email", nullable=True)
    phone_owner:str

class Payments(SQLModel, table=True):
    __tablename__ = "payments"

    payment_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    payment_method: str = Field(nullable=False)
    payment_status: Optional[str] = Field(nullable=False)
    payment_date: Optional[datetime] = Field(datetime.now, nullable=True)
    total_amount: Decimal 
    order_item_id :int

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    order_item_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.user_id")
    items_list: List[Dict] = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    status:str =Field(nullable=True)

class ShippingTable(SQLModel, table=True):
    __tablename__ = "shipping"

    shipping_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str
    phone: str
    address: str
    province: str
    payment_id: Optional[int] = Field(default=None, foreign_key="payments.payment_id")
    status: str

class UserFollowShop(SQLModel, table=True):
    __tablename__ = "user_follow_shop"

    user_id: int = Field(foreign_key="users.user_id", primary_key=True)
    shop_name_id: int = Field(foreign_key="shop_name.shop_name_id", primary_key=True)
    followed_at: date


class SearchEvent(SQLModel, table=True):
    __tablename__ = "search_event"

    search_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.user_id")
    keyword: Optional[str]   
    created_at: Optional[date] = Field(default_factory=date.today, nullable=True)

class ViewProductEvent(SQLModel, table=True):
    __tablename__ = "view_product_event"

    view_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.user_id")
    product_id: int = Field(foreign_key="products.product_id")
    shop_name_id:Optional[int] 
    name: Optional[str]
    created_at: Optional[date] = Field(default_factory=date.today, nullable=True)


class ViewCategoryEvent(SQLModel, table=True):
    __tablename__ = "view_category_event"

    view_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.user_id")
    category_id: int = Field(foreign_key="categories.category_id") 
    name: Optional[str]
    created_at: Optional[date] = Field(default_factory=date.today, nullable=True)


class Keyword(BaseModel):
    user_id: int
    keyword: str

class LoginData(BaseModel):
    email: str
    password: str

class ordertList(BaseModel):
    ordertList: List[Dict] 
    user_id: int

class StatusUpdate(BaseModel):
    user_id: int
    status_update:str

class Shipping(BaseModel):
    name: str
    phone: str
    address: str
    province: str    

class PaymentAndShipping(BaseModel):
    paymentdata:Payments
    shippingdata:Shipping
    orderItemId:int

class Comment(BaseModel):
    user_id: int
    product_id:int
    comment_content:str

class ChangePasswordData(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str
    user_id:int

class RegisterData(BaseModel):
    name: str
    email: str
    password: str

class RegisterShopData(BaseModel):
    shop_name: str
    shop_address: str
    email_owner: str
    phone_owner: str



class OrderItemId(BaseModel):
    order_item_id: int

class DataUpdate(BaseModel):
    name: Optional[str]
    phone_number:Optional[str]
    gender: Optional[str]
    birthday: Optional[str]

class PayLoad(BaseModel):
    user_id: int
    data: DataUpdate

class FollowShopRequest(BaseModel):
    user_id: int
    shop_name_id: int

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token:str
    new_password: str

class Token(BaseModel):
    token: str

class Email(BaseModel):
    email: str

class DeleteProductData(BaseModel):
    product_id: int
    image: str
    category_id:int



class ProductAdd(BaseModel):
    shop_name_id:int
    product_name: str
    price:int
    description:str
    category_id:int
    image:str
    description_detail:str

class ProductUpdate(BaseModel):
    shop_name_id:int
    product_name: str
    product_id:int
    price:int
    description:str
    category_id:int
    description_detail:str

class SMSRequest(BaseModel):
    phone_number: str


class ViewProduct(BaseModel):
     user_id:int
     product_id:int
     name:str

class ViewCategory(BaseModel):
     user_id:int
     category_id:int
     name:str


