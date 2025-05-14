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
    # Bước 1: Tìm trong bảng Category dựa vào name == keyword
    statement = (
        select(Carts, Products,ShopName)  # Lấy dữ liệu từ cả Orders và Products
        .join(Products, Carts.product_id == Products.product_id)
        .join(ShopName,Products.shop_name_id == ShopName.shop_name_id)  # Kết hợp theo product_id
        .where(Carts.user_id == user_id)  # Điều kiện lọc theo user_id
    )
     
    results = session.exec(statement).all()

    orders_with_products = []
    for row in results:
        cart, product, shop_name = row  # Tách giá trị từ đối tượng Row
        orders_with_products.append({
            "order_id":cart.cart_id,
            "product_id":product.product_id,
            "product_name": product.description,
            "price": product.price,  # Thuộc tính từ bảng Products
            "product_image": product.image,
            "shop_name":shop_name.name
                # Thuộc tính từ bảng Products
            # Thêm các thuộc tính khác từ bảng Orders và Products nếu cần
        })

    # Nếu không tìm thấy category, trả về lỗi 404
    if not orders_with_products:
        return []
    return orders_with_products   


@router.get("/get-amount-item-of-cart-by-user-id/{user_id}")
def get_item_type_count_of_cart_by_user_id(user_id: int, session: Session = Depends(get_session)) -> Any:
    # Truy vấn số loại item trong giỏ hàng theo user_id
    statement = (
        select(func.count(distinct(Carts.product_id))).where(Carts.user_id == user_id)
    )
    
    # Lấy kết quả số loại item
    item_type_count = session.exec(statement).first()
    
    # Kiểm tra nếu không có item nào
    if item_type_count is None:
        item_type_count = 0
    
    return item_type_count





@router.post("/add-product-to-cart-by-productid")
def order_product(order:Carts,session: Session = Depends(get_session)) -> Any:

    existing_cart_item = session.query(Carts).filter(
        Carts.user_id == order.user_id,
        Carts.product_id == order.product_id
    ).first()
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
    
    print("Order deleted successfully")
    return {"message": "Order deleted successfully"}
