"""
Run once to seed roles, permissions, and create the first admin user.

Usage:
  python seed_rbac.py
"""
from app.config.db import SessionLocal
from app.models.rbac import Role, Permission, UserRole, RolePermission
from app.models.user import User

db = SessionLocal()

# ── 1. Permissions ──────────────────────────────────────────────────────────
ALL_PERMISSIONS = [
    ("product:create",      "Add new products"),
    ("product:update",      "Edit existing products"),
    ("product:delete",      "Delete products"),
    ("category:create",     "Add new categories"),
    ("category:update",     "Edit categories"),
    ("category:delete",     "Delete categories"),
    ("order:read_all",      "View all orders"),
    ("order:update_status", "Change order status"),
    ("user:manage_roles",   "Assign / remove roles from users"),
]

perm_map: dict[str, Permission] = {}
for name, desc in ALL_PERMISSIONS:
    existing = db.query(Permission).filter(Permission.name == name).first()
    if not existing:
        p = Permission(name=name, description=desc)
        db.add(p)
        db.flush()
        perm_map[name] = p
    else:
        perm_map[name] = existing

# ── 2. Roles ────────────────────────────────────────────────────────────────
def get_or_create_role(name: str, description: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if not role:
        role = Role(name=name, description=description)
        db.add(role)
        db.flush()
    return role

admin_role   = get_or_create_role("admin",   "Full access to everything")
manager_role = get_or_create_role("manager", "Manage products, categories, orders")

# ── 3. Role → Permissions ────────────────────────────────────────────────────
ROLE_PERMISSIONS = {
    "admin":   [p[0] for p in ALL_PERMISSIONS],          # admin gets ALL
    "manager": [
        "product:create", "product:update",
        "category:create", "category:update",
        "order:read_all", "order:update_status",
    ],
}

for role_obj in [admin_role, manager_role]:
    for perm_name in ROLE_PERMISSIONS[role_obj.name]:
        perm = perm_map[perm_name]
        exists = db.query(RolePermission).filter(
            RolePermission.role_id == role_obj.id,
            RolePermission.permission_id == perm.id
        ).first()
        if not exists:
            db.add(RolePermission(role_id=role_obj.id, permission_id=perm.id))

# ── 4. Assign admin role to the first user ───────────────────────────────────
# Change this email to your actual first admin user's email
ADMIN_EMAIL = "admin@gmail.com"

first_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
if first_admin:
    already = db.query(UserRole).filter(
        UserRole.user_id == first_admin.id,
        UserRole.role_id == admin_role.id
    ).first()
    if not already:
        db.add(UserRole(user_id=first_admin.id, role_id=admin_role.id))
        print(f"✓ Admin role assigned to '{ADMIN_EMAIL}'")
    else:
        print(f"  '{ADMIN_EMAIL}' already has admin role")
else:
    print(f"  User '{ADMIN_EMAIL}' not found — sign up first, then re-run this script")

db.commit()
db.close()
print("Seed complete.")
