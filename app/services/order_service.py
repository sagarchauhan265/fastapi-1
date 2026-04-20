import razorpay
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product

CANCELLABLE_STATUSES = {"pending", "confirmed"}


def _get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _get_effective_price(product: Product) -> int:
    if product.offer_price and product.offer_price > 0:
        return product.offer_price
    return product.price


def place_order_service(user_id: int, shipping_address: str | None, notes: str | None, db: Session) -> dict:
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="CART_IS_EMPTY")

    total_amount = 0

    # Validate cart (no stock deduction yet — happens after payment)
    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"PRODUCT_NOT_FOUND: {cart_item.product_id}")
        if product.is_active != 1:
            raise HTTPException(status_code=400, detail=f"PRODUCT_NOT_ACTIVE: {product.name}")
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"INSUFFICIENT_STOCK: {product.name} (available: {product.stock})",
            )
        total_amount += _get_effective_price(product) * cart_item.quantity

    # Create a pending order (no items yet)
    order = Order(
        user_id=user_id,
        status="pending",
        payment_status="unpaid",
        total_amount=total_amount,
        shipping_address=shipping_address,
        notes=notes,
    )
    db.add(order)
    db.flush()

    # Create Razorpay order (amount in paise)
    rzp_client = _get_razorpay_client()
    print(f"Creating ",rzp_client)
    rzp_order = rzp_client.order.create({
        "amount": total_amount * 100,
        "currency": "INR",
        "receipt": f"order_{order.id}",
        "payment_capture": 1,
    })

    order.razorpay_order_id = rzp_order["id"]
    db.commit()
    db.refresh(order)

    return {
        "order_id": order.id,
        "razorpay_order_id": rzp_order["id"],
        "amount": total_amount * 100,
        "currency": "INR",
        "key_id": settings.RAZORPAY_KEY_ID,
    }


def verify_payment_service(
    user_id: int,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    db: Session,
) -> Order:
    order = (
        db.query(Order)
        .filter(Order.razorpay_order_id == razorpay_order_id, Order.user_id == user_id)
        .with_for_update()
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")
    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="PAYMENT_ALREADY_VERIFIED")

    # Verify Razorpay signature
    rzp_client = _get_razorpay_client()
    try:
        rzp_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })
    except Exception:
        order.payment_status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail="INVALID_PAYMENT_SIGNATURE")

    # Re-read cart and fulfill — lock products atomically
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="CART_IS_EMPTY")

    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).with_for_update().first()
        if not product or product.stock < cart_item.quantity:
            raise HTTPException(status_code=400, detail=f"STOCK_CHANGED: {cart_item.product_id}")

        unit_price = _get_effective_price(product)
        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            unit_price=unit_price,
            quantity=cart_item.quantity,
            subtotal=unit_price * cart_item.quantity,
        ))
        product.stock -= cart_item.quantity

    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()

    order.payment_status = "paid"
    order.status = "confirmed"
    order.razorpay_payment_id = razorpay_payment_id
    order.razorpay_signature = razorpay_signature
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
