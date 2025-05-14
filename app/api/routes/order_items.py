
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import StatusUpdate,OrderItem,ordertList, Payments,OrderItemId
from app.core.db import get_session




router = APIRouter()

@router.post("/create-order-items-by-userid")
def create_order_items(data:ordertList, session: Session = Depends(get_session)) -> Any:
    
    new_order_item = OrderItem(
            user_id=data.user_id,
            items_list=data.ordertList,
            status='pending'
        )
    session.add(new_order_item)
    session.commit()
    session.refresh(new_order_item)
    return {"message": "OrderItems created successfully",
            "order_item_id": new_order_item.order_item_id
            }

@router.get("/get-order-items-by-userid/{user_id}")
def get_order_items_by_user_id(user_id: int, session: Session = Depends(get_session)) -> Any:
    # Thực hiện JOIN giữa OrderItem và Product dựa trên product_id và lọc với status 'pending'
    statement = (
        select(OrderItem)
        .where((OrderItem.user_id == user_id) & (OrderItem.status == 'pending'))
    )
    
    results = session.exec(statement).first()
    
    if not results:
        raise HTTPException(status_code=404, detail="No pending products found for this user")
    
    # Định dạng kết quả trả về
    
    return results


@router.get("/get-purchase-order-by-userid/{user_id}")
def get_order_items_by_user_id(user_id: int, session: Session = Depends(get_session)) -> Any:
    # Thực hiện JOIN giữa OrderItem và Product dựa trên product_id và lọc với status 'pending'
    statement = (
        select(OrderItem,Payments)
        .join(Payments,Payments.order_item_id == OrderItem.order_item_id)
        .where(
            (OrderItem.user_id == user_id) & 
            (OrderItem.status == 'success')
            )
    )
    
    results = session.exec(statement).all()
    
    response = []
    for order_item, payment in results:
        response.append({
            "order_item": order_item,
            "payment": payment
        })

    if not results:
        raise HTTPException(status_code=404, detail="No pending products found for this user")
    
    # Định dạng kết quả trả về
    
    return response




@router.put("/update_order_items_status-by-userid")
def update_order_items_status(status:StatusUpdate,session: Session = Depends(get_session)
):
    # Lấy order item theo ID
    statement = select(OrderItem).where((OrderItem.user_id == status.user_id)&(OrderItem.status == 'pending'))
    order_item =session.exec(statement).first()
    # Nếu không tồn tại thì trả về lỗi
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")

    # Cập nhật cột status 
    order_item.status = status.status_update
    session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
      # Tải lại dữ liệu của order_item

    return order_item

@router.put("/delete-purchase-order-status-by-orderitemid")
def delete_purchase_order_status_purchase_status(data:OrderItemId,session: Session = Depends(get_session)
):
    # Lấy order item theo ID
    statement = select(OrderItem).where(OrderItem.order_item_id == data.order_item_id)
    order_item =session.exec(statement).first()
    # Nếu không tồn tại thì trả về lỗi
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")

    # Cập nhật cột status 
    order_item.status = 'delete'
    session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
      # Tải lại dữ liệu của order_item

    return  {"message": "OrderItems delete successfully !!"}