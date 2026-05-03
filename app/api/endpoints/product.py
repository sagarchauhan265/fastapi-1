from datetime import datetime, timedelta
from fastapi import APIRouter,Form,File,Body,Depends,HTTPException,Query
from fastapi.responses import JSONResponse
from app.config.settings import settings
from app.middleware.upload_file_middleware import validate_file
from app.schema.response import ApiResponse
from pydantic import  ValidationError
from sqlalchemy.orm import Session
from app.services.product_service import get_product_list_by_category_service, get_product_list_service, get_product_by_id_service, product_add_service, bulk_product_upload_service, delete_product_service, update_product_service
from app.schema.productschema import ProductBase, ProductResponse, ProductUpdate,CategoryByProductResponse
from app.schema.bulkschema import BulkUploadResult
from app.utils.excel_helper import parse_excel
from app.config.db import get_db
from app.middleware.rate_limit_middleware import limiter
from fastapi import Request,UploadFile
from app.middleware.verify_jwt import verify_jwt
from app.utils.cloudinary_helper import upload_image, delete_image
from app.config.redis import redis_client
from typing import Optional
import json

#auth_router = APIRouter(dependencies=[Depends(limiter.limit("5/minute"))]) 
product_router = APIRouter()  # Apply rate limit to all routes in this router
#response_model=ApiResponse[List[ProductResponse]]
#product_router = APIRouter(dependencies=[Depends(verify_jwt)]) 
# @product_router.post("/add_product",response_model=ApiResponse[ProductResponse],dependencies=[Depends(verify_jwt)])
@product_router.post("/add_product",response_model=ApiResponse[ProductResponse],dependencies=[Depends(verify_jwt)])
#@limiter.limit("1/minute")
async def product_add(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    product_image:UploadFile = Depends(validate_file),
    sku: str = Form(None),
    stock: int = Form(...),
    unit: str = Form(...),
    is_active: bool = Form(...),
    offer_price: int = Form(None),
    cat_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # inside product_add endpoint, before ProductBase(...)
        image_bytes = await product_image.read()
        image_url = upload_image(image_bytes)
        product = ProductBase(
            name=name,
            description=description,
            price=price ,
            product_image=image_url ,
            sku=sku,
            stock=stock,
            unit=unit,
            is_active=is_active,
            offer_price=offer_price,
            cat_id=cat_id
            )
    except ValidationError as e:
        errors = [{"field": err["loc"][0] if err["loc"] else "unknown", "message": err["msg"]} for err in e.errors()]
        raise HTTPException(
            status_code=400,
            detail=ApiResponse(
                success=False,
                message="Validation Error",
                error=errors
            ).model_dump(exclude={"data"})
        )
    result = product_add_service(product, db)
    return JSONResponse(
        status_code=201,
        content=ApiResponse(
            success=True,
            message="Product added successfully",
            data=ProductResponse.model_validate(result)
        ).model_dump(mode="json", exclude_none=True)
    )

# @product_router.get("/get_product_list",response_model=ApiResponse[ProductResponse],dependencies=[Depends(verify_jwt)])
@product_router.get("/get_product/{product_id}", response_model=ApiResponse[ProductResponse])
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    result = get_product_by_id_service(product_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Product fetched successfully",
            data=ProductResponse.model_validate(result)
        ).model_dump(mode="json", exclude_none=True)
    )


@product_router.post("/bulk_upload_products", response_model=ApiResponse[BulkUploadResult],dependencies=[Depends(verify_jwt)])
async def bulk_upload_products(
    file: UploadFile,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="ONLY_XLSX_FILES_ALLOWED")

    file_bytes = await file.read()
    rows = parse_excel(file_bytes)
    result = bulk_product_upload_service(rows, db)

    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Bulk upload completed",
            data=result
        ).model_dump(mode="json", exclude_none=True)
    )


@product_router.delete("/delete_product/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    image_url = delete_product_service(product_id, db)
    if image_url:
        delete_image(image_url)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Product deleted successfully"
        ).model_dump(mode="json", exclude_none=True)
    )


@product_router.post("/update_product/{product_id}", response_model=ApiResponse[ProductResponse])
async def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    sku: str = Form(None),
    stock: int = Form(None),
    unit: str = Form(None),
    is_active: bool = Form(None),
    offer_price: int = Form(None),
    cat_id: int = Form(None),
    product_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    new_image_url = None
    if product_image and product_image.filename:
        allowed = ["image/jpeg", "image/png", "image/jpg"]
        if product_image.content_type not in allowed:
            raise HTTPException(status_code=400, detail="INVALID_FILE_TYPE")
        image_bytes = await product_image.read()
        if len(image_bytes) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="FILE_TOO_LARGE")
        new_image_url = upload_image(image_bytes)

    update_data = {
        "name": name,
        "description": description,
        "price": price,
        "sku": sku,
        "stock": stock,
        "unit": unit,
        "is_active": is_active,
        "offer_price": offer_price,
        "cat_id": cat_id,
        **({"product_image": new_image_url} if new_image_url else {}),
    }

    result, replaced_image = update_product_service(product_id, update_data, db)

    if replaced_image:
        delete_image(replaced_image)

    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Product updated successfully",
            data=ProductResponse.model_validate(result)
        ).model_dump(mode="json", exclude_none=True)
    )


@product_router.get("/get_product_list",response_model=ApiResponse[ProductResponse])
async def get_product_list(
request: Request,
# action:str=Query(..., min_length=1, max_length=50),
page:int=1,
q:Optional[str] = None,
price_min: Optional[float] = None,
price_max: Optional[float] = None,
db: Session = Depends(get_db)
):
    print(q,page)
    redis_key = "product_list_cache"
    cached_data = redis_client.get(redis_key)
    print(cached_data)
    if cached_data:
        print("Cache hit for product list")
        try:
         product_ids = json.loads(cached_data)  # ✅ no decode
        except json.JSONDecodeError:
         print("Invalid cache, clearing...")
         #redis_client.delete(redis_key)
         #product_ids = None
        return JSONResponse(
            status_code=200,
            content=ApiResponse(
                success=True,
                message="Product list fetched successfully (from cache)",
                current_page=page,
                data=[ProductResponse.model_validate(p) for p in product_ids]
            ).model_dump(mode="json", exclude_none=True)
        )
       
    result, total_pages, page = get_product_list_service(db,page,q,price_min,price_max)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Product list fetched successfully",
            current_page=page,          # ← already a field in ApiResponse
            total_page=total_pages,
            data=[ProductResponse.model_validate(p) for p in result]
        ).model_dump(mode="json", exclude_none=True)
    )   

@product_router.get("/category_by_id/{cat_id}")
async def get_product_list(
    cat_id: int,
    db: Session = Depends(get_db),
    currentUser:dict = Depends(verify_jwt)
    ):

    results = get_product_list_by_category_service(cat_id, db)
    _,category = results[0] # Get category details from the first result
    # for product, _ in results:
    #     print("product", 
    #            product.id,
    #            product.name,
    #            product.cat_id,
    #            product.created_at,
    #            product.updated_at,
    #            product.product_image,
    #            product.sku,
    #            product.stock,
    #            product.unit,
    #            product.is_active,
    #            product.offer_price,
    #            product.description,
    #            product.price

    #            )
    #     break
   
   
   
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Product list fetched successfully",
            data=CategoryByProductResponse(
                id=category.id,
                cat_name=category.cat_name,
                cat_title=category.cat_title,
                cat_slug=category.cat_slug,
                product=[ProductResponse.model_validate(product) for product, _ in results]
            )
        ).model_dump(mode="json",exclude_none=True)
    )  

