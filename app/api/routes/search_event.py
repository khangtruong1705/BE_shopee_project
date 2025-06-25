from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.models import SearchEvent,Keyword
from app.core.db import get_session
from sqlmodel import Session

router = APIRouter()



@router.post("/add-search-by-keyword")
def add_keyword(data:Keyword,session: Session = Depends(get_session)) -> Any:
    try:
        new_search = SearchEvent(
            user_id=data.user_id,
            keyword=data.keyword)
        
        session.add(new_search)
        session.commit()
        session.refresh(new_search)
        return {"message": "Add Search-Keyword successfully"} 
    except:
        raise HTTPException(status_code=400, detail="Add Search-Keyword Fail !!!")

    