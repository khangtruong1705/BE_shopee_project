from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select,func
from app.models import ShopName, Products,UserFollowShop
from typing import Any
from app.core.db import get_session

router = APIRouter()


@router.get("/get-shop-name-by-productid/{product_id}")
def get_shop_name_by_product_id(product_id,session: Session = Depends(get_session)) -> Any:


    statement = (
            select(ShopName)
            .join(Products, Products.shop_name_id == ShopName.shop_name_id)
            .where(Products.product_id == int(product_id))
        )   
    shop_name = session.exec(statement).first()

        # Kiểm tra nếu không tìm thấy kết quả
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

        # Kiểm tra nếu không tìm thấy kết quả
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