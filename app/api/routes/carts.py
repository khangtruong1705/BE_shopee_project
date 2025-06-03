from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Carts,Products,ShopName
from app.core.db import get_session
from sqlmodel import Session, func, select
from sqlalchemy import distinct


router = APIRouter()



@router.get("/get-cart-by-userid/{user_id}")
def get_orders_by_user_id(user_id:int,session: Session = Depends(get_session)) -> Any:
    statement = (
        select(Carts, Products,ShopName) 
        .join(Products, Carts.product_id == Products.product_id)
        .join(ShopName,Products.shop_name_id == ShopName.shop_name_id)  
        .where(Carts.user_id == user_id) 
    )
    results = session.exec(statement).all()
    orders_with_products = []
    for row in results:
        cart, product, shop_name = row 
        orders_with_products.append({
            "order_id":cart.cart_id,
            "product_id":product.product_id,
            "product_name": product.description,
            "price": product.price, 
            "product_image": product.image,
            "shop_name":shop_name.name
        })
    if not orders_with_products:
        return []
    return orders_with_products   

@router.get("/get-amount-item-of-cart-by-user-id/{user_id}")
def get_item_type_count_of_cart_by_user_id(user_id: int, session: Session = Depends(get_session)) -> Any:
    statement = (
        select(func.count(distinct(Carts.product_id))).where(Carts.user_id == user_id)
    )
    item_type_count = session.exec(statement).first()
    if item_type_count is None:
        item_type_count = 0
    return item_type_count

@router.post("/add-product-to-cart-by-productid")
def order_product(order:Carts,session: Session = Depends(get_session)) -> Any:
    statement = select(Carts).where(
    Carts.user_id == order.user_id,
    Carts.product_id == order.product_id)
    existing_cart_item = session.exec(statement).first()
    if existing_cart_item:
        raise HTTPException(status_code=400, detail="The product is already in the cart!!!")
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@router.delete("/delete-order-product-by-orderid/{order_id}")
def delete_order(order_id: int, session: Session = Depends(get_session)) -> Any:
    order = session.get(Carts, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(order)
    session.commit()
    return {"message": "Order deleted successfully"}
