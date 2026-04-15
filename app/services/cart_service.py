from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.product import Product


def _get_effective_price(product: Product) -> int:
    if product.offer_price and product.offer_price > 0:
        return product.offer_price
    return product.price


def add_to_cart_service(user_id: int, product_id: int, quantity: int,cart_action:str, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="PRODUCT_NOT_FOUND")
    if product.is_active != 1:
        raise HTTPException(status_code=400, detail="PRODUCT_NOT_ACTIVE")
    if quantity > 1:
        raise HTTPException(status_code=400, detail="UPDATE_MAX_QUANTITY_1")

    existing_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
        .first()
    )

    if existing_item:
        cart_action = cart_action.lower()
        if cart_action == "increase":
         new_quantity = existing_item.quantity + quantity
        elif cart_action == "decrease":
            new_quantity = existing_item.quantity - quantity
        else:
            raise HTTPException(status_code=400, detail="INVALID_CART_ACTION")  
        if new_quantity > product.stock:
            raise HTTPException(status_code=400, detail="INSUFFICIENT_STOCK")
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        if quantity > product.stock:
            raise HTTPException(status_code=400, detail="INSUFFICIENT_STOCK")
        new_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item


# def get_cart_service(user_id: int, db: Session):
    
#     items = db.query(Product, CartItem).join(CartItem, Product.id == CartItem.product_id).filter(CartItem.user_id == user_id).all()
#     cart_items = []
#     total = 0

#     for item in items:
#         product = db.query(Product).filter(Product.id == item.product_id).first()
#         if not product:
#             continue
#         price = _get_effective_price(product)
#         subtotal = price * item.quantity
#         total += subtotal
#         cart_items.append({
#             "id": item.id,
#             "PrdocutDetail": [product.id, product.name, product.cat_id, product.created_at, product.updated_at, product.product_image, price, product.offer_price, product.stock, product.unit, product.is_active, product.description],
#             # "name": product.name,
#             "price": price,
#             "quantity": item.quantity,
#             "subtotal": subtotal,
#             "created_at": item.created_at,
#             "updated_at": item.updated_at,
#         })

#     return {"items": cart_items, "total": total}
def get_cart_service(user_id: int, db: Session):
    # Unpack tuples correctly from the join
    items = (
        db.query(Product, CartItem)
        .join(CartItem, Product.id == CartItem.product_id)
        .filter(CartItem.user_id == user_id)
        .all()
    )
    cart_items = []
    total = 0

    for product, cart_item in items:         
        price = _get_effective_price(product)
        subtotal = price * cart_item.quantity
        subdiscount = (product.price - price) * cart_item.quantity
        total += subtotal

        cart_items.append({
            "id": cart_item.id,
            "product_id": product.id,
            "name": product.name,             
            "quantity": cart_item.quantity,
            "subtotal": subtotal,
            "total_discount": subdiscount, 
            "created_at": cart_item.created_at,
            "updated_at": cart_item.updated_at,
            "product": {                    
                "id": product.id,
                "name": product.name,
                "cat_id": product.cat_id,           
                "sku": product.sku,                
                "product_image": product.product_image,  
                "price": product.price,
                "offer_price": product.offer_price,
                "stock": product.stock,
                "unit": product.unit,
                "is_active": product.is_active,
                "description": product.description,
                "currency":"INR",
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            },
        })

    return {"items": cart_items, "total": total}


def update_cart_item_service(user_id: int, item_id: int, quantity: int, db: Session):
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="CART_ITEM_NOT_FOUND")
    if item.user_id != user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product.is_active != 1:
        raise HTTPException(status_code=400, detail="PRODUCT_NOT_ACTIVE")
    if quantity > product.stock:
        raise HTTPException(status_code=400, detail="INSUFFICIENT_STOCK")

    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def remove_cart_item_service(user_id: int, item_id: int, db: Session):
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="CART_ITEM_NOT_FOUND")
    if item.user_id != user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    db.delete(item)
    db.commit()


def clear_cart_service(user_id: int, db: Session):
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
