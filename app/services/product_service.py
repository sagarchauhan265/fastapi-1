from app.models.product import Product
from app.models.category import Category
from app.schema.productschema import ProductBase
from app.schema.bulkschema import BulkRowError, BulkUploadResult
from passlib.context import CryptContext
from fastapi import HTTPException
from pydantic import ValidationError

def product_add_service(product,db):
    if(db.query(Product).filter(Product.name == product.name).first()):
        raise HTTPException(status_code=400, detail="PRODUCT_ALREADY_EXISTS")
    if product.sku and db.query(Product).filter(Product.sku == product.sku).first():
        raise HTTPException(status_code=400, detail="SKU_ALREADY_EXISTS")
    
    new_product = Product(
        name = product.name,
        description = product.description,
        price = product.price,
        product_image = product.product_image,
        sku = product.sku,
        stock = product.stock,
        unit = product.unit,
        is_active = product.is_active,
        offer_price = product.offer_price,
        cat_id = product.cat_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def get_product_by_id_service(product_id, db):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="PRODUCT_NOT_FOUND")
    return product




def delete_product_service(product_id: int, db):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="PRODUCT_NOT_FOUND")
    image_url = product.product_image
    db.delete(product)
    db.commit()
    return image_url


def update_product_service(product_id: int, update_data: dict, db):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="PRODUCT_NOT_FOUND")

    # Check name uniqueness if name is being updated
    new_name = update_data.get("name")
    if new_name and new_name != product.name:
        if db.query(Product).filter(Product.name == new_name).first():
            raise HTTPException(status_code=400, detail="PRODUCT_NAME_ALREADY_EXISTS")

    # Check SKU uniqueness if sku is being updated
    new_sku = update_data.get("sku")
    if new_sku and new_sku != product.sku:
        if db.query(Product).filter(Product.sku == new_sku).first():
            raise HTTPException(status_code=400, detail="SKU_ALREADY_EXISTS")

    old_image_url = product.product_image

    for field, value in update_data.items():
        if value is not None:
            setattr(product, field, value)

    db.commit()
    db.refresh(product)

    # Return old image url so endpoint can delete it from Cloudinary if replaced
    new_image = update_data.get("product_image")
    replaced_image = old_image_url if new_image and old_image_url else None

    return product, replaced_image


def get_product_list_service(db):
    limit = 2
    offset = 0
    # products = db.query(Product).limit(limit).offset(offset).all()
    products = db.query(Product).all()
    return products


def _coerce_row(row: dict) -> dict:
    """Coerce and sanitize raw Excel cell values before Pydantic validation."""

    # Trim all string fields
    for key, val in row.items():
        if isinstance(val, str):
            row[key] = val.strip() or None

    # Coerce float → int for numeric fields (Excel stores numbers as float)
    for int_field in ("price", "stock", "cat_id", "offer_price"):
        val = row.get(int_field)
        if isinstance(val, float):
            row[int_field] = int(val)

    # Coerce is_active: accept bool, int, or string "true"/"false"/"yes"/"no"/"1"/"0"
    is_active_val = row.get("is_active")
    if isinstance(is_active_val, bool):
        pass  # already bool
    elif isinstance(is_active_val, (int, float)):
        row["is_active"] = bool(int(is_active_val))
    elif isinstance(is_active_val, str):
        row["is_active"] = is_active_val.lower() in ("true", "1", "yes")

    return row


def _validate_row_business_rules(product: ProductBase, row_num: int) -> list[BulkRowError]:
    """Apply business-rule validations that go beyond Pydantic type checks."""
    errors = []

    # Whitespace-only string fields
    for field in ("name", "description", "unit"):
        val = getattr(product, field, None)
        if val is not None and not val.strip():
            errors.append(BulkRowError(row=row_num, field=field, message=f"{field.upper()}_CANNOT_BE_BLANK"))

    # price must be > 0
    if product.price is not None and product.price <= 0:
        errors.append(BulkRowError(row=row_num, field="price", message="PRICE_MUST_BE_GREATER_THAN_0"))

    # stock must be >= 0
    if product.stock is not None and product.stock < 0:
        errors.append(BulkRowError(row=row_num, field="stock", message="STOCK_CANNOT_BE_NEGATIVE"))

    # offer_price must be > 0 and < price
    if product.offer_price is not None:
        if product.offer_price <= 0:
            errors.append(BulkRowError(row=row_num, field="offer_price", message="OFFER_PRICE_MUST_BE_GREATER_THAN_0"))
        elif product.price and product.offer_price >= product.price:
            errors.append(BulkRowError(row=row_num, field="offer_price", message="OFFER_PRICE_MUST_BE_LESS_THAN_PRICE"))

    # Field length limits (matching DB column sizes)
    length_limits = {"name": 100, "description": 255, "sku": 255, "unit": 50}
    for field, limit in length_limits.items():
        val = getattr(product, field, None)
        if val and len(val) > limit:
            errors.append(BulkRowError(row=row_num, field=field, message=f"{field.upper()}_MAX_LENGTH_{limit}_EXCEEDED"))

    return errors


def bulk_product_upload_service(rows: list[dict], db) -> BulkUploadResult:
    errors: list[BulkRowError] = []
    products_to_insert: list[Product] = []

    #cloumns =  ["name", "description", "price", "product_image", "sku", "stock", "unit", "is_active", "offer_price", "cat_id"]

    # Load lookup sets from DB once — avoid N+1 queries
    existing_names = {p.name for p in db.query(Product.name).all()}
    existing_skus = {p.sku for p in db.query(Product.sku).filter(Product.sku.isnot(None)).all()}

    from app.models.category import Category
    valid_cat_ids = {c.id for c in db.query(Category.id).all()}

    # Within-batch duplicate tracking
    batch_names: set[str] = set()
    batch_skus: set[str] = set()

    for row in rows:
        row_num = row.pop("_row")
        row = _coerce_row(row)

        # --- Pydantic type + required field validation ---
        try:
            product = ProductBase(**row)
        except ValidationError as e:
            for err in e.errors():
                errors.append(BulkRowError(
                    row=row_num,
                    field=str(err["loc"][0]) if err["loc"] else None,
                    message=err["msg"]
                ))
            continue

        # --- Business rule validation ---
        rule_errors = _validate_row_business_rules(product, row_num)
        if rule_errors:
            errors.extend(rule_errors)
            continue

        # --- cat_id must exist in category table ---
        if product.cat_id not in valid_cat_ids:
            errors.append(BulkRowError(row=row_num, field="cat_id", message="CATEGORY_NOT_FOUND"))
            continue

        # --- Duplicate name: DB + within-batch ---
        if product.name in existing_names or product.name in batch_names:
            errors.append(BulkRowError(row=row_num, field="name", message="PRODUCT_ALREADY_EXISTS"))
            continue

        # --- Duplicate SKU: DB + within-batch ---
        if product.sku:
            if product.sku in existing_skus or product.sku in batch_skus:
                errors.append(BulkRowError(row=row_num, field="sku", message="SKU_ALREADY_EXISTS"))
                continue
            batch_skus.add(product.sku)

        batch_names.add(product.name)
        products_to_insert.append(Product(
            name=product.name,
            description=product.description,
            price=product.price,
            product_image=product.product_image,
            sku=product.sku,
            stock=product.stock,
            unit=product.unit,
            is_active=product.is_active,
            offer_price=product.offer_price,
            cat_id=product.cat_id,
        ))

    if products_to_insert:
        db.add_all(products_to_insert)
        db.commit()

    return BulkUploadResult(
        success_count=len(products_to_insert),
        failed_count=len(errors),
        errors=errors,
    )


def get_product_list_by_category_service(cat_id, db):
    results = (
            db.query(Product, Category)
            .join(Category, Product.cat_id == Category.id)
            .filter(Product.cat_id == cat_id)
            .all()
        )
    if not results:
        raise HTTPException(status_code=404, detail="NO_PRODUCTS_FOUND_FOR_CATEGORY")
    return results
