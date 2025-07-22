from fastapi import APIRouter, Depends, HTTPException,status,UploadFile,File,Form
from sqlmodel import Session, select,func
from app.models import ShopName,Users, Products,UserFollowShop,RegisterShopData,Email
from typing import Any
from app.core.db import get_session
import time
import cloudinary
import cloudinary.uploader


router = APIRouter()



@router.post("/register-shop")
def register_shop(data:RegisterShopData,session: Session = Depends(get_session)):
    
        statement = select(ShopName).where(ShopName.email_owner ==data.email_owner)
        existing_shop = session.exec(statement).first()
        if existing_shop is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered !!!")
        find_user_id_owner_statement =select(Users).where(Users.email ==data.email_owner)
        user_id_owner = session.exec(find_user_id_owner_statement).first()
        new_shop = ShopName(
            name=data.shop_name,
            rate=0,
            category_id=None,
            image='',
            response_rate=0,
            email_owner=data.email_owner,
            phone_owner=data.phone_owner,
            user_id_owner = user_id_owner.user_id
        )
        session.add(new_shop)
        session.commit()
        return {"detail": "Shop registered successfully !!!"}


@router.post("/check-existing-shop")
def check_existing_shop(data:Email,session: Session = Depends(get_session)):
    
        statement = select(ShopName).where(ShopName.email_owner ==data.email)
        existing_shop = session.exec(statement).first()
        if existing_shop:
            return True
        if existing_shop is None:
            return False
            

@router.get("/get-shop-by-email-owner/{email}")
def get_user_by_id(email: str, session: Session = Depends(get_session)) -> Any:
    statement = select(ShopName).where(ShopName.email_owner == email)
    shop = session.exec(statement).first()
    if shop is None:
        raise HTTPException(status_code=404, detail=f"Shop with email {email} not found.")
   
    return shop


@router.post("/upload-shop-avatar-by-shopid")
async def upload_shop_avatar(shop_name_id: int = Form(...), avatar: UploadFile = File(...),session: Session = Depends(get_session)):
    statement = select(ShopName).where(ShopName.shop_name_id == shop_name_id)
    shop =session.exec(statement).first()
    contents = await avatar.read()
    unix_timestamp = int(time.time())
    if not shop.image:
        # Upload file to Cloudinary
            result = cloudinary.uploader.upload(
            contents,
            folder="shop_avatars",
            public_id=f"{shop_name_id}_{unix_timestamp}",  
            resource_type="image"
    )          
    if shop.image :
        filename = shop.image.rpartition('/')[2].split('.')[0]
        public_id = f"shop_avatars/{filename}" 
        cloudinary.uploader.destroy(public_id, resource_type="image")
        result =  cloudinary.uploader.upload(
            contents,
            folder="shop_avatars",
            public_id=f"{shop_name_id}_{unix_timestamp}", 
            resource_type="image")
    shop.image = result["secure_url"]
    session.commit()
    session.refresh(shop)
    return {
        "avatar_url": result["secure_url"]
    }


@router.get("/get-shop-name-by-productid/{product_id}")
def get_shop_name_by_product_id(product_id,session: Session = Depends(get_session)) -> Any:
    statement = (
            select(ShopName)
            .join(Products, Products.shop_name_id == ShopName.shop_name_id)
            .where(Products.product_id == int(product_id))
        )   
    shop_name = session.exec(statement).first()
    if not shop_name:
            raise HTTPException(
                status_code=404, 
                detail=f"No shop found for product_id {product_id}"
            )
    return shop_name

@router.get("/get-shop-name-by-shopnameid/{shop_name_id}")
def get_shop_name_by_product_id(shop_name_id:int,session: Session = Depends(get_session)) -> Any:
    statement = (
            select(ShopName)
            .where(ShopName.shop_name_id == int(shop_name_id))
        )   
    shop_name = session.exec(statement).first()
    if not shop_name:
            raise HTTPException(
                status_code=404, 
                detail=f"No shop found for shop_name {shop_name_id}"
            )
    return shop_name

@router.get("/get-product-shop-amount-by-shopnameid/{shop_id}")
def count_products_by_shopnameid(shop_id, session: Session = Depends(get_session)):
    statement = select(func.count()).where(Products.shop_name_id == int(shop_id))
    result = session.exec(statement)
    count = result.one()  
    return count

@router.get("/get-user-follow-amount-by-shopnameid/{shop_id}")
def count_user_follow_by_shopnameid(shop_id, session: Session = Depends(get_session)):
    statement = select(func.count()).where(UserFollowShop.shop_name_id == int(shop_id))
    result = session.exec(statement)
    count = result.one()  
    return count