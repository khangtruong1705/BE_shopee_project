from fastapi import APIRouter

from app.api.routes import products,users,comments,shop_name,order_items,carts,payments,user_follow_shop

api_router = APIRouter()
# api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(shop_name.router, prefix="/shop-name", tags=["shop_name"])
api_router.include_router(order_items.router, prefix="/order-items", tags=["order_items"])
api_router.include_router(carts.router, prefix="/carts", tags=["carts"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(user_follow_shop.router, prefix="/user-follow-shop", tags=["user_follow_shop"])
