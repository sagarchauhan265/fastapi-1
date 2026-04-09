from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse,ORJSONResponse
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.middleware.verify_jwt import verify_jwt
from app.schema.categoryschema import CategoryCreate, CategoryResponse
from app.schema.response import ApiResponse
from app.services.category_service import (
    add_category_service,
    get_category_list_service,
    get_category_by_id_service,
    update_category_service,
    delete_category_service,
)

category_router = APIRouter()


@category_router.post("/add", response_class=ORJSONResponse, response_model=ApiResponse[CategoryResponse],dependencies=[Depends(verify_jwt)])
async def add_category(
    payload: CategoryCreate,
      db: Session = Depends(get_db),
      currentUser:dict = Depends(verify_jwt)
      ):
    result = add_category_service(payload, db,currentUser)
    return ORJSONResponse(
        status_code=201,
        content=ApiResponse(
            success=True,
            message="Category created successfully",
            data=CategoryResponse.model_validate(result)
        ).model_dump(mode="json", exclude_none=True)
    )


@category_router.get("/list", response_model=ApiResponse[CategoryResponse])
async def get_category_list(db: Session = Depends(get_db)):
    result = get_category_list_service(db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Category list fetched successfully",
            data=[CategoryResponse.model_validate(c) for c in result]
        ).model_dump(mode="json", exclude_none=True)
    )


@category_router.get("/{category_id}", response_model=ApiResponse[CategoryResponse])
async def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    result = get_category_by_id_service(category_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Category fetched successfully",
            data=CategoryResponse.model_validate(result)
        ).model_dump(mode="json", exclude_none=True)
    )


@category_router.post("/update/{category_id}", response_model=ApiResponse[CategoryResponse],dependencies=[Depends(verify_jwt)])
async def update_category(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db), currentUser:dict = Depends(verify_jwt)):
    result = update_category_service(category_id, payload, db,currentUser)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Category updated successfully",
            data=CategoryResponse.model_validate(result)
        ).model_dump(mode="json", exclude_none=True)
    )


@category_router.delete("/delete/{category_id}",dependencies=[Depends(verify_jwt)])
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    delete_category_service(category_id, db)
    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="Category deleted successfully",
        ).model_dump(mode="json", exclude_none=True)
    )
