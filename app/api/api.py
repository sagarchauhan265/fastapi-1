from fastapi import APIRouter
from app.api.endpoints.auth import auth_router
from app.api.endpoints.product import product_router
from app.api.endpoints.category import category_router
from app.api.endpoints.cart import cart_router
from app.api.endpoints.order import order_router

main_router = APIRouter()


main_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
    )
main_router.include_router(
    product_router,
    prefix="/product",
    tags=["Product"]
    )
main_router.include_router(
    category_router,
    prefix="/category",
    tags=["Category"]
    )
main_router.include_router(
    cart_router,
    prefix="/cart",
    tags=["Cart"]
    )
main_router.include_router(
    order_router,
    prefix="/order",
    tags=["Order"]
    )