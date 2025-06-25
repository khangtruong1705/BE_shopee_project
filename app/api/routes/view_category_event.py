from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.models import ViewCategoryEvent,ViewCategory
from app.core.db import get_session
from sqlmodel import Session

router = APIRouter()



@router.post("/add-view-by-categoryid")
def add_category_view(data:ViewCategory,session: Session = Depends(get_session)) -> Any:
    try: 
        new_view = ViewCategoryEvent(
            user_id=data.user_id,
            category_id=data.category_id,
            name= data.name
            )

        session.add(new_view)
        session.commit()
        session.refresh(new_view)
        return {"message": "Add New-View successfully"} 
    except:
        session.rollback()
        raise HTTPException(status_code=400, detail="Add New-View Fail !!!")

    