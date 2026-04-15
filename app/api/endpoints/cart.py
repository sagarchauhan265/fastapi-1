from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.middleware.verify_jwt import verify_jwt
from app.schema.cartschema import (
    AddToCartRequest,
    UpdateCartItemRequest,
    CartItemResponse,
    CartResponse,
)
from app.schema.response import ApiResponse
from app.services.cart_service import (
    add_to_cart_service,
    get_cart_service,
    update_cart_item_service,
    remove_cart_item_service,
    clear_cart_service,
)
from app.models.product import Product

cart_router = APIRouter(dependencies=[Depends(verify_jwt)])


@cart_router.post("/add", response_model=ApiResponse[CartItemResponse])
async def add_to_cart(
    body: AddToCartRequest,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    item = add_to_cart_service(user_id, body.product_id, body.quantity,body.cart_action, db)
    product = db.query(Product).filter(Product.id == item.product_id).first()
    price = product.offer_price if product.offer_price and product.offer_price > 0 else product.price
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Cart updated successfully",
            data=CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                name=product.name,
                price=price,
                quantity=item.quantity,
                subtotal=price * item.quantity,
                created_at=item.created_at,
                updated_at=item.updated_at,
            ),
        ).model_dump(mode="json", exclude_none=True),
    )


@cart_router.get("", response_model=ApiResponse[CartResponse])
async def get_cart(
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    cart_data = get_cart_service(user_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Cart fetched successfully",
            data=CartResponse(**cart_data),
        ).model_dump(mode="json", exclude_none=True),
    )


@cart_router.patch("/item/{item_id}", response_model=ApiResponse[CartItemResponse])
async def update_cart_item(
    item_id: int,
    body: UpdateCartItemRequest,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    item = update_cart_item_service(user_id, item_id, body.quantity, db)
    product = db.query(Product).filter(Product.id == item.product_id).first()
    price = product.offer_price if product.offer_price and product.offer_price > 0 else product.price
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Cart item updated successfully",
            data=CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                name=product.name,
                price=price,
                quantity=item.quantity,
                subtotal=price * item.quantity,
                created_at=item.created_at,
                updated_at=item.updated_at,
            ),
        ).model_dump(mode="json", exclude_none=True),
    )


@cart_router.delete("/item/{item_id}")
async def remove_cart_item(
    item_id: int,
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    remove_cart_item_service(user_id, item_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Item removed from cart",
        ).model_dump(mode="json", exclude_none=True),
    )


@cart_router.delete("/clear")
async def clear_cart(
    payload: dict = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    user_id = payload["id"]
    clear_cart_service(user_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Cart cleared successfully",
        ).model_dump(mode="json", exclude_none=True),
    )
