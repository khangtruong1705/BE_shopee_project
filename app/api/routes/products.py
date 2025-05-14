from datetime import datetime
from typing import Any
from unidecode import unidecode
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlmodel import Session, select,func
from app.models import Products,Categories
from app.core.db import engine,get_session
# from confluent_kafka import Producer
import json



# KAFKA_SERVER = 'localhost:9092'
# producer_config = {
#     'bootstrap.servers': KAFKA_SERVER
# }

# producer = Producer(producer_config)
current_date = datetime.now().strftime('%Y-%m-%d')

router = APIRouter()




@router.get("/get-all-products")
def get_all_products(
    page: int = Query(1, ge=1),  # Mặc định page=1, phải >= 1
    limit: int = Query(12, ge=1),  # Mặc định limit=12, phải >= 1, không giới hạn tối đa
    session: Session = Depends(get_session)
) -> Any:
    # Đếm tổng số sản phẩm
    total_statement = select(func.count()).select_from(Products)
    total = session.exec(total_statement).one()

    # Lấy sản phẩm theo phân trang
    statement = select(Products).offset((page - 1) * limit).limit(limit)
    results = session.exec(statement).all()

    # Trả về dữ liệu kèm thông tin phân trang
    return {
        "results": results,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/get-products-by-search/{keyword}")
def get_products_by_search(keyword,session: Session = Depends(get_session)) -> Any:
    normalized_keyword = unidecode(keyword)
    message_content = {
        "search_keyword": keyword,
        "timestamp": current_date
    }
    serialized_value = json.dumps(message_content).encode('utf-8')
    # producer.produce('search_topic', value=serialized_value)
    # producer.flush() 
    print("Message sent to Kafka:", serialized_value)
    statement_product = select(Products).where(Products.detailed_description.ilike(f"%{keyword}%"))
    
    products = session.exec(statement_product).all()
    
   
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    
    return products

@router.get("/get-products-by-category/{name}")
def get_products_by_search(name,session: Session = Depends(get_session)) -> Any:
     # Bước 1: Tìm trong bảng Category dựa vào name == keyword
    statement_category = select(Categories).where(Categories.name == name)
    category = session.exec(statement_category).first()
    
    # Nếu không tìm thấy category, trả về lỗi 404
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    
    message_content = {
        "category_name": category.name,
        "timestamp": current_date
    }
    serialized_value = json.dumps(message_content).encode('utf-8')
    # producer.produce('category_topic', value=serialized_value)
    # producer.flush() 
    print("Message sent to Kafka:", serialized_value)
    
    # Bước 2: Sử dụng item_id để tìm trong bảng Products
    statement_product = select(Products).where(Products.category_id == category.category_id)
    products = session.exec(statement_product).all()
    
    # Nếu không có sản phẩm nào trong bảng products tương ứng với category đó
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    return products   


@router.get("/get-product-by-productid/{product_id}")
def get_products_by_id(product_id,session: Session = Depends(get_session)) -> Any:


    statement_product = select(Products).where(Products.product_id ==int(product_id))
    
    product = session.exec(statement_product).first()
    
   
    if not product:
        raise HTTPException(status_code=404, detail="No products found for this category")
    
    message_content = {
        "product_id" : product.product_id,
        "product_name": product.name,
        "timestamp": current_date
    }
    serialized_value = json.dumps(message_content).encode('utf-8')
    # producer.produce('product_topic', value=serialized_value)
    # producer.flush() 
    return product

@router.get("/get-top-views-products")
def get_top_views_products(session: Session = Depends(get_session)) -> Any:
    statement = select(Products).order_by(Products.views.desc()).limit(18)
    results = session.exec(statement).all()
    return results


@router.get("/get-products-same-category-by-productid/{product_id}")
def get_products_same_category_by_productid(product_id:int,session: Session = Depends(get_session)) -> Any:
     # Bước 1: Tìm trong bảng Category dựa vào name == keyword
    statement = select(Products).where(Products.product_id == int(product_id) )
    product = session.exec(statement).first()
    # Nếu không tìm thấy category, trả về lỗi 404
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    
   
    # Bước 2: Sử dụng item_id để tìm trong bảng Products
    statement_product = select(Products).where(Products.category_id == product.category_id)
    products = session.exec(statement_product).all()
    
    # Nếu không có sản phẩm nào trong bảng products tương ứng với category đó
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    return products 


