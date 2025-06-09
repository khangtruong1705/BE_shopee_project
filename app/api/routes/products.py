from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlmodel import Session, select,func
from app.models import Products,Categories
from app.core.db import get_session
from dotenv import load_dotenv
import json
# from confluent_kafka import Producer

load_dotenv()
current_date = datetime.now().strftime('%Y-%m-%d')


# KAFKA_SERVER = 'localhost:9092'
# producer_config = {
#     'bootstrap.servers': KAFKA_SERVER
# }
# producer = Producer(producer_config)




router = APIRouter()




@router.get("/get-all-products")
def get_all_products( page: int = Query(1, ge=1),limit: int = Query(12, ge=1), session: Session = Depends(get_session)) -> Any:
    total_statement = select(func.count()).select_from(Products)
    total = session.exec(total_statement).one()
    statement = select(Products).offset((page - 1) * limit).limit(limit)
    results = session.exec(statement).all()
    return {
        "results": results,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/get-products-by-search/{keyword}")
def get_products_by_search(keyword,session: Session = Depends(get_session)) -> Any:
    message_content = {
        "search_keyword": keyword,
        "timestamp": current_date
    }
    serialized_value = json.dumps(message_content).encode('utf-8')
    # producer.produce('search_topic', value=serialized_value)
    # producer.flush() 
    print("Message sent to Kafka:", serialized_value)
    statement_product = select(Products).where(Products.description.ilike(f"%{keyword}%"))
    products = session.exec(statement_product).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    return products

@router.get("/get-products-by-category/{name}")
def get_products_by_category(name,session: Session = Depends(get_session)) -> Any:
    statement_category = select(Categories).where(Categories.name == name)
    category = session.exec(statement_category).first()
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
    statement_product = select(Products).where(Products.category_id == category.category_id)
    products = session.exec(statement_product).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    return products   

@router.get("/get-product-by-productid/{product_id}")
def get_products_by_id(product_id,session: Session = Depends(get_session)) -> Any:
    statement_product = select(Products).where(Products.product_id ==int(product_id))
    product = session.exec(statement_product).first()
    if not product:
        raise HTTPException(status_code=404, detail="No products found for this category")
    # message_content = {
    #     "product_id" : product.product_id,
    #     "product_name": product.name,
    #     "timestamp": current_date
    # }
    # serialized_value = json.dumps(message_content).encode('utf-8')
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
    statement = select(Products).where(Products.product_id == int(product_id) )
    product = session.exec(statement).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    statement_product = select(Products).where(Products.category_id == product.category_id)
    products = session.exec(statement_product).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    return products 


