from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.models import ViewProduct,ViewProductEvent,Products
from app.core.db import get_session
from sqlmodel import Session, select

router = APIRouter()





@router.post("/add-view-by-productid")
def add_product_view(data:ViewProduct,session: Session = Depends(get_session)) -> Any:
    try:

        statement = select(Products).where(Products.product_id == data.product_id)
        product = session.exec(statement).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        new_view = ViewProductEvent(
            user_id=data.user_id,
            product_id=data.product_id,
            name = data.name,
            shop_name_id=product.shop_name_id
            )
        product.views += 1
        session.add(new_view)
        session.commit()
        session.refresh(new_view)
        return {"message": "Add New-View successfully"} 
    except:
        session.rollback()
        raise HTTPException(status_code=400, detail="Add New-View Fail !!!")

    