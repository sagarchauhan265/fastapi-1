from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.config.db import get_db
from app.middleware.verify_jwt import require_permission
from app.models.rbac import Role, UserRole
from app.models.user import User
from app.schema.response import ApiResponse

admin_router = APIRouter()


class AssignRoleRequest(BaseModel):
    user_id: int
    role_name: str  # "admin", "manager", etc.


class UserRoleResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    roles: list[str]


@admin_router.post(
    "/assign-role",
    response_model=ApiResponse[UserRoleResponse],
    dependencies=[Depends(require_permission("user:manage_roles"))],
)
def assign_role(body: AssignRoleRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    role = db.query(Role).filter(Role.name == body.role_name).first()
    if not role:
        raise HTTPException(404, f"Role '{body.role_name}' not found")

    already_assigned = db.query(UserRole).filter(
        UserRole.user_id == body.user_id,
        UserRole.role_id == role.id
    ).first()

    if not already_assigned:
        db.add(UserRole(user_id=body.user_id, role_id=role.id))
        db.commit()

    # Return updated roles list
    user_roles = db.query(UserRole).filter(UserRole.user_id == body.user_id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message=f"Role '{body.role_name}' assigned to user '{user.name}'",
            data=UserRoleResponse(
                user_id=user.id,
                user_name=user.name,
                user_email=user.email,
                roles=[r.name for r in roles],
            ).model_dump()
        ).model_dump(mode="json", exclude_none=True)
    )


@admin_router.delete(
    "/remove-role",
    response_model=ApiResponse[UserRoleResponse],
    dependencies=[Depends(require_permission("user:manage_roles"))],
)
def remove_role(body: AssignRoleRequest, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.name == body.role_name).first()
    if not role:
        raise HTTPException(404, f"Role '{body.role_name}' not found")

    user_role = db.query(UserRole).filter(
        UserRole.user_id == body.user_id,
        UserRole.role_id == role.id
    ).first()

    if not user_role:
        raise HTTPException(400, f"User does not have role '{body.role_name}'")

    db.delete(user_role)
    db.commit()

    user = db.query(User).filter(User.id == body.user_id).first()
    remaining_roles = db.query(UserRole).filter(UserRole.user_id == body.user_id).all()
    role_ids = [ur.role_id for ur in remaining_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message=f"Role '{body.role_name}' removed from user '{user.name}'",
            data=UserRoleResponse(
                user_id=user.id,
                user_name=user.name,
                user_email=user.email,
                roles=[r.name for r in roles],
            ).model_dump()
        ).model_dump(mode="json", exclude_none=True)
    )


@admin_router.get(
    "/user/{user_id}/roles",
    response_model=ApiResponse[UserRoleResponse],
    dependencies=[Depends(require_permission("user:manage_roles"))],
)
def get_user_roles(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    return JSONResponse(
        status_code=200,
        content=ApiResponse(
            success=True,
            message="User roles fetched",
            data=UserRoleResponse(
                user_id=user.id,
                user_name=user.name,
                user_email=user.email,
                roles=[r.name for r in roles],
            ).model_dump()
        ).model_dump(mode="json", exclude_none=True)
    )
