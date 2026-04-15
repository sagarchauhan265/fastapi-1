from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.middleware.verify_jwt import verify_jwt
from app.models.order import Order
from app.schema.orderschema import (
    PlaceOrderRequest,
    CheckoutResponse,
    VerifyPaymentRequest,
    OrderResponse,
    OrderListResponse,
    OrderSummaryResponse,
)
from app.schema.response import ApiResponse
from app.services.invoice_service import generate_invoice_pdf
from app.models.order import OrderItem
from app.services.order_service import (
    place_order_service,
    verify_payment_service,
    get_orders_service,
    get_order_detail_service,
    cancel_order_service,
)

order_router = APIRouter(dependencies=[Depends(verify_jwt)])


@order_router.post("/checkout", response_model=ApiResponse[CheckoutResponse])
async def place_order(
    body: PlaceOrderRequest,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    checkout_data = place_order_service(user_id, body.shipping_address, body.notes, db)
    return JSONResponse(
        status_code=201,
        content=ApiResponse(
            success=True,
            message="Order created. Complete payment to confirm.",
            data=CheckoutResponse(**checkout_data),
        ).model_dump(mode="json", exclude_none=True),
    )


@order_router.post("/verify-payment", response_model=ApiResponse[OrderResponse])
async def verify_payment(
    body: VerifyPaymentRequest,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    user_name = payload["name"]
    user_email = payload["email"]
    order = verify_payment_service(user_id, body.razorpay_order_id, body.razorpay_payment_id, body.razorpay_signature, db)
    order_data = get_order_detail_service(user_id, user_name, user_email, order.id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Payment verified. Order confirmed.",
            data=OrderResponse(**order_data),
        ).model_dump(mode="json", exclude_none=True),
    )


@order_router.get("/{order_id}/invoice")
async def get_invoice(
    order_id: int,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    user_name = payload["name"]
    user_email = payload["email"]
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        return JSONResponse(status_code=404, content={"success": False, "message": "ORDER_NOT_FOUND"})
    if order.payment_status != "paid":
        return JSONResponse(status_code=400, content={"success": False, "message": "INVOICE_UNAVAILABLE: ORDER_NOT_PAID"})
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    item_dicts = [
        {
            "product_name": i.product_name,
            "product_sku": i.product_sku,
            "unit_price": i.unit_price,
            "quantity": i.quantity,
            "subtotal": i.subtotal,
        }
        for i in items
    ]
    pdf_bytes = generate_invoice_pdf(
        order_id=order.id,
        user_name=user_name,
        user_email=user_email,
        shipping_address=order.shipping_address,
        razorpay_payment_id=order.razorpay_payment_id,
        total_amount=order.total_amount,
        items=item_dicts,
        created_at=order.created_at,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{order_id}.pdf"},
    )


@order_router.get("", response_model=ApiResponse[OrderListResponse])
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    user_name = payload["name"]
    user_email = payload["email"]
    result = get_orders_service(user_id,user_name,user_email, page, page_size, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Orders fetched successfully",
            data=OrderListResponse(
                orders=[OrderSummaryResponse(**o) for o in result["orders"]],
                total=result["total"],
                page=result["page"],
                page_size=result["page_size"],
            ),
        ).model_dump(mode="json", exclude_none=True),
    )


@order_router.get("/{order_id}", response_model=ApiResponse[OrderResponse])
async def get_order(
    order_id: int,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    user_name = payload["name"]
    user_email = payload["email"]
    order_data = get_order_detail_service(user_id,user_name,user_email, order_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Order fetched successfully",
            data=OrderResponse(**order_data),
        ).model_dump(mode="json", exclude_none=True),
    )


@order_router.patch("/{order_id}/cancel", response_model=ApiResponse[OrderResponse])
async def cancel_order(
    order_id: int,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    user_name = payload["name"]
    user_email = payload["email"]
    cancel_order_service(user_id, order_id, db)
    order_data = get_order_detail_service(user_id, user_name, user_email, order_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Order cancelled successfully",
            data=OrderResponse(**order_data),
        ).model_dump(mode="json", exclude_none=True),
    )
