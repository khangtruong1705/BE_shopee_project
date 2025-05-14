from datetime import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.models import Payments,PaymentAndShipping,Shipping,ShippingTable
from app.core.db import get_session





router = APIRouter()





@router.post("/create-payment-and-shipping", response_model=Payments)
def create_payment_and_shipping(data:PaymentAndShipping, session: Session = Depends(get_session)):
    # Khởi tạo đối tượng Payment
    new_payment = Payments(
        payment_method=data.paymentdata.payment_method,
        payment_status=data.paymentdata.payment_status,
        payment_date=datetime.utcnow(),
        total_amount=data.paymentdata.total_amount,
        order_item_id = data.orderItemId
    )
    
    # Thêm Payment vào session và commit để lấy payment_id
    session.add(new_payment)
    session.commit()
    session.refresh(new_payment)

    # Khởi tạo đối tượng Shipping với payment_id từ new_payment
    new_shipping = ShippingTable(
        name=data.shippingdata.name,
        phone=data.shippingdata.phone,
        address=data.shippingdata.address,
        province=data.shippingdata.province,
        payment_id=new_payment.payment_id, # Lấy payment_id từ đối tượng mới tạo
        status = 'pending'
    )

    # Thêm Shipping vào session và commit
    session.add(new_shipping)
    session.commit()
    session.refresh(new_shipping)

    return new_payment