from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models import Comments,Comment
from typing import Any, List
from app.core.db import get_session

router = APIRouter()
 

@router.get("/get-comments-by-productid/{product_id}", response_model=List[Comments])
def get_comments_by_product(product_id: int, session: Session = Depends(get_session)) -> Any:
    statement = select(Comments).where(Comments.product_id == product_id)
    comments = session.exec(statement).all()
    if not comments:
        return []
    return comments

@router.post("/add-comment-by-productid", response_model=Comments)
def add_comment(comment: Comment, session: Session = Depends(get_session)) -> Any:
    new_comment = Comments(
        product_id=comment.product_id,
        user_id=comment.user_id,
        comment_content=comment.comment_content,
    )
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)  
    return new_comment