from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.middleware.verify_jwt import verify_jwt
from app.schema.orderschema import (
    PlaceOrderRequest,
    OrderResponse,
    OrderListResponse,
    OrderSummaryResponse,
)
from app.schema.response import ApiResponse
from app.services.order_service import (
    place_order_service,
    get_orders_service,
    get_order_detail_service,
    cancel_order_service,
)

order_router = APIRouter(dependencies=[Depends(verify_jwt)])


@order_router.post("/checkout", response_model=ApiResponse[OrderResponse])
async def place_order(
    body: PlaceOrderRequest,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    order = place_order_service(user_id, body.shipping_address, body.notes, db)
    order_data = get_order_detail_service(user_id, order.id, db)
    return JSONResponse(
        status_code=201,
        content=ApiResponse(
            success=True,
            message="Order placed successfully",
            data=OrderResponse(**order_data),
        ).model_dump(mode="json", exclude_none=True),
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
    cancel_order_service(user_id, order_id, db)
    order_data = get_order_detail_service(user_id, order_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Order cancelled successfully",
            data=OrderResponse(**order_data),
        ).model_dump(mode="json", exclude_none=True),
    )
