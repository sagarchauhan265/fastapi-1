from fastapi import APIRouter
product_router = APIRouter()

@product_router.get("/")
def get_products():
    return {
         "message":"get products"
    }

@product_router.post("/")
def add_products():
    return {"message":"add products"}

@product_router.delete("/{id}")
def  delete_product():
    return {"message":"add products"}





