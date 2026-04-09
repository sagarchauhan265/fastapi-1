from fastapi import HTTPException
from app.models.category import Category
def add_category_service(payload, db,currentUser):
    existing = db.query(Category).filter(
        (Category.cat_slug == payload.cat_slug) | (Category.cat_name == payload.cat_name)
    ).first()

    if existing:
        if existing.cat_slug == payload.cat_slug:
            raise HTTPException(status_code=400, detail="CATEGORY_SLUG_ALREADY_EXISTS")
        raise HTTPException(status_code=400, detail="CATEGORY_NAME_ALREADY_EXISTS")
    new_category = Category(
        cat_name=payload.cat_name,
        cat_title=payload.cat_title,
        cat_slug=payload.cat_slug,
        create_by=currentUser.get("name")
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def get_category_list_service(db):
    return db.query(Category).all()


def get_category_by_id_service(category_id, db):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="CATEGORY_NOT_FOUND")
    return category


def update_category_service(category_id, payload, db,currentUser):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="CATEGORY_NOT_FOUND")
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="NO_FIELDS_TO_UPDATE")
    if "cat_slug" in updates:
        existing = db.query(Category).filter(Category.cat_slug == updates["cat_slug"], Category.id != category_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="CATEGORY_SLUG_ALREADY_EXISTS")
    if "cat_name" in updates:
        existing = db.query(Category).filter(Category.cat_name == updates["cat_name"], Category.id != category_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="CATEGORY_NAME_ALREADY_EXISTS")

    for field, value in updates.items():
        setattr(category, field, value)
    category.update_by = currentUser.get("name")
    db.commit()
    db.refresh(category)
    return category


def delete_category_service(category_id, db):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="CATEGORY_NOT_FOUND")
    db.delete(category)
    db.commit()
