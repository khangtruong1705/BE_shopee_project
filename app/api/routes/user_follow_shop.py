from fastapi import APIRouter, Depends, HTTPException,status
from app.models import FollowShopRequest,UserFollowShop
from sqlmodel import Session, select
from app.core.db import get_session
from datetime import datetime
router = APIRouter()


@router.post("/toggle-follow")
def toggle_follow(data: FollowShopRequest, session: Session = Depends(get_session)):
    existing_follow = session.exec(
        select(UserFollowShop).where(
            UserFollowShop.user_id == data.user_id,
            UserFollowShop.shop_name_id == data.shop_name_id
        )
    ).first()

    if existing_follow:
        session.delete(existing_follow)
        session.commit()
        return {"message": "Unfollowed", "is_following": False}
    else:
        new_follow = UserFollowShop(
            user_id=data.user_id,
            shop_name_id=data.shop_name_id,
            followed_at=datetime.utcnow()
        )
        session.add(new_follow)
        session.commit()
        return {"message": "Followed", "is_following": True}



@router.get("/check-follow")
def check_follow(user_id: int, shop_name_id: int, session: Session = Depends(get_session)):
    follow = session.exec(
        select(UserFollowShop).where(
            UserFollowShop.user_id == user_id,
            UserFollowShop.shop_name_id == shop_name_id
        )
    ).first()
    return {"is_following": bool(follow)}


