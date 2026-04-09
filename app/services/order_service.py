from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product

CANCELLABLE_STATUSES = {"pending", "confirmed"}


def _get_effective_price(product: Product) -> int:
    if product.offer_price and product.offer_price > 0:
        return product.offer_price
    return product.price


def place_order_service(user_id: int, shipping_address: str | None, notes: str | None, db: Session) -> Order:
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="CART_IS_EMPTY")

    order_items_data = []
    total_amount = 0

    # Validate stock and lock products inside the same transaction
    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).with_for_update().first()
        if not product:
            raise HTTPException(status_code=400, detail=f"PRODUCT_NOT_FOUND: {cart_item.product_id}")
        if product.is_active != 1:
            raise HTTPException(status_code=400, detail=f"PRODUCT_NOT_ACTIVE: {product.name}")
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"INSUFFICIENT_STOCK: {product.name} (available: {product.stock})",
            )

        unit_price = _get_effective_price(product)
        subtotal = unit_price * cart_item.quantity
        total_amount += subtotal

        order_items_data.append({
            "product": product,
            "product_id": product.id,
            "product_name": product.name,
            "product_sku": product.sku,
            "unit_price": unit_price,
            "quantity": cart_item.quantity,
            "subtotal": subtotal,
        })

    # Create order
    order = Order(
        user_id=user_id,
        status="pending",
        total_amount=total_amount,
        shipping_address=shipping_address,
        notes=notes,
    )
    db.add(order)
    db.flush()  # get order.id before committing

    # Create order items and deduct stock atomically
    for data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=data["product_id"],
            product_name=data["product_name"],
            product_sku=data["product_sku"],
            unit_price=data["unit_price"],
            quantity=data["quantity"],
            subtotal=data["subtotal"],
        )
        db.add(order_item)
        data["product"].stock -= data["quantity"]

    # Clear the cart
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()

    db.commit()
    db.refresh(order)
    return order


def get_orders_service(user_id: int,user_name:str,user_email:str, page: int, page_size: int, db: Session) -> dict:
    offset = (page - 1) * page_size
    query = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc())
    total = query.count()
    orders = query.offset(offset).limit(page_size).all()

    summaries = []
    for order in orders:
        item_count = db.query(OrderItem).filter(OrderItem.order_id == order.id).count()
        summaries.append({
            "id": order.id,
            "name": user_name,
            "email": user_email,
            "status": order.status,
            "total_amount": order.total_amount,
            "item_count": item_count,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        })

    return {"orders": summaries, "total": total, "page": page, "page_size": page_size}


def get_order_detail_service(user_id: int,user_name:str,user_email:str, order_id: int, db: Session) -> dict:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    return {
        "id": order.id,
        "name": user_name,
        "email": user_email,
        "status": order.status,
        "total_amount": order.total_amount,
        "shipping_address": order.shipping_address,
        "notes": order.notes,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "product_sku": item.product_sku,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
            }
            for item in items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


def cancel_order_service(user_id: int, order_id: int, db: Session) -> Order:
    order = db.query(Order).filter(Order.id == order_id).with_for_update().first()
    if not order:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    if order.status not in CANCELLABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"ORDER_CANNOT_BE_CANCELLED: current status is '{order.status}'",
        )

    # Restore stock for each order item
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
        if product:
            product.stock += item.quantity

    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order
