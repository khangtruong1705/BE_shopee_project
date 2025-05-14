from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Comments,Comment
from typing import Any, List
from app.core.db import get_session

router = APIRouter()
 

@router.get("/get-comments-by-productid/{product_id}", response_model=List[Comments])
def get_comments_by_product(product_id: int, session: Session = Depends(get_session)) -> Any:
    # Truy vấn bình luận theo product_id
    statement = select(Comments).where(Comments.product_id == product_id)
    comments = session.exec(statement).all()

    # Nếu không tìm thấy bình luận, trả về lỗi 404
    if not comments:
        return []

    return comments

@router.post("/add-comment-by-productid", response_model=Comments)
def add_comment(comment: Comment, session: Session = Depends(get_session)) -> Any:
    # Tạo một bản ghi bình luận mới
    new_comment = Comments(
        product_id=comment.product_id,
        user_id=comment.user_id,
        comment_content=comment.comment_content,
    )
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)  # Lấy dữ liệu mới nhất sau khi thêm

    return new_comment