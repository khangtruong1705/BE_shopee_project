from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException,Query,UploadFile,File,Form
from sqlmodel import Session, select,func
from app.models import Products,Categories,ProductAdd,DeleteProductData,ProductUpdate
from app.core.db import get_session
from dotenv import load_dotenv
import json
import time
import cloudinary
import cloudinary.uploader

# from confluent_kafka import Producer

load_dotenv()
current_date = datetime.now().strftime('%Y-%m-%d')


# KAFKA_SERVER = 'localhost:9092'
# producer_config = {
#     'bootstrap.servers': KAFKA_SERVER
# }
# producer = Producer(producer_config)




router = APIRouter()


@router.get("/ping", methods=["GET","HEAD"])
def ping():
    print('Ping!!!!!')
    return {"status": "ok"}




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


@router.get("/get-all-categories")
def get_all_categories( session: Session = Depends(get_session)) -> Any:
    statement = select(Categories)
    categories = session.exec(statement).all() 
    return categories


@router.put("/edit-product-by-productid")
def update_product(data: ProductUpdate, session: Session = Depends(get_session)):
    # Tìm product theo product_id
    statement = select(Products).where(Products.product_id == data.product_id)
    product = session.exec(statement).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Cập nhật các field
    product.name = data.product_name
    product.shop_name_id = data.shop_name_id
    product.price = data.price
    product.description = data.description
    product.category_id = data.category_id
    product.detailed_description = data.description_detail

    session.add(product)
    session.commit()
    session.refresh(product)

    return {"message": "Product updated successfully!"}


@router.post("/add-product")
def add_product(data:ProductAdd ,session: Session = Depends(get_session)):
        new_product = Products(
            name=data.product_name,
            image ='',
            description = data.description,
            price = data.price,
            rating = 0,
            sold = 0,
            detailed_description = data.description_detail,
            category_id = data.category_id,
            shop_name_id = data.shop_name_id,
            updated_at = None,
            views=0
        )
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product

@router.delete("/delete-product-by-productid")
def delete_product_by_productid(data:DeleteProductData,session: Session = Depends(get_session)
):
    statement = select(Products).where(Products.product_id == data.product_id)
    product =session.exec(statement).first()
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    if not data.image:
        pass
    if data.image:
        filename = data.image.rpartition('/')[2].split('.')[0]
        public_id = f"product_avatar/{data.category_id}/{filename}" 
        cloudinary.uploader.destroy(public_id, resource_type="image")  
    session.delete(product)
    session.commit()  
    return  {"message": "Product delete successfully !!"}

@router.post("/upload-product-avatar")
async def upload_product_avatar(product_id: int = Form(...),
                                category_id: int = Form(...),
                                 avatar: UploadFile = File(...),
                                 session: Session = Depends(get_session)
):
    statement = select(Products).where(Products.product_id == product_id)
    product =session.exec(statement).first()
    contents = await avatar.read()
    unix_timestamp = int(time.time())
    if not product.image:
        # Upload file to Cloudinary
            result = cloudinary.uploader.upload(
            contents,
            folder=f"product_avatar/{category_id}",
            public_id=f"{product_id}_{unix_timestamp}",  
            resource_type="image"
    )          
    if product.image :
        filename = product.image.rpartition('/')[2].split('.')[0]
        public_id = f"product_avatar/{category_id}/{filename}"
        cloudinary.uploader.destroy(public_id, resource_type="image")
        result =  cloudinary.uploader.upload(
            contents,
            folder=f"product_avatar/{category_id}",
            public_id=f"{product_id}_{unix_timestamp}", 
            resource_type="image")
    product.image = result["secure_url"]
    session.commit()
    session.refresh(product)
    return {
        "avatar_url": result["secure_url"]
    }


@router.get("/get-products-by-shop-name-id")
def get_products_by_shop_name_id(shop_name_id:int = Query(...),session: Session = Depends(get_session)) -> Any:
    statement_product = select(Products).where(Products.shop_name_id ==shop_name_id)
    products = session.exec(statement_product).all()
    return products

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


