from fastapi import APIRouter
from app.api.endpoints.auth import auth_router
from app.api.endpoints.product import product_router
main_router = APIRouter()


main_router.include_router(
    auth_router,
    prefix="/auth"
    )
main_router.include_router(
    product_router,
    prefix="/product"
    )