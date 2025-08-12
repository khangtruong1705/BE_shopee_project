from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import OrderItemsTable,PaymentTable,SearchMessage,ShippingTable,ViewCategoryMessage,ViewProductMessage
from app.core.db import get_warehouse_session
from sqlmodel import Session, func, select,text
from sqlalchemy import distinct


router = APIRouter()



@router.get("/get-views-products-by-shopid/{shop_id}")
def get_views_products_by_shopid(
    shop_id: int,
    session: Session = Depends(get_warehouse_session)
):
    sql_statement = text("""
        SELECT name,  COUNT(name) AS view_count
        FROM view_product_message
        WHERE shop_name_id = :shop_id
        AND created_at >= now() - interval '2 month'
        GROUP BY name
    """)
    results = session.execute(sql_statement, {"shop_id": shop_id}).all()
    return [
    {"view_count": r.view_count, "name": r.name}
    for r in results
]

@router.get("/get-payment-data")
def get_views_products_by_shopid(
    session: Session = Depends(get_warehouse_session)
):
    sql_statement = text("""
        SELECT payment_method,COUNT(payment_method) AS payment_method_count,SUM(total_amount) AS total_amount 
        FROM payment_table
        GROUP BY payment_method                
    """)
    results = session.execute(sql_statement).all()
    return [
    {"payment_method": r.payment_method,"total_amount": r.total_amount,"payment_method_count": r.payment_method_count}
    for r in results
]


@router.get("/get-shipping-data")
def get_views_products_by_shopid(
    session: Session = Depends(get_warehouse_session)
):
    sql_statement = text("""
        SELECT province,COUNT(province) AS province_area_count
        FROM shipping_table
        GROUP BY province                
    """)
    results = session.execute(sql_statement).all()
    return [
    {"province": r.province,"province_area_count": r.province_area_count}
    for r in results
]


