from fastapi import APIRouter, HTTPException, Query
from app.api.v1.handlers import admin_handler
from pydantic import BaseModel

router = APIRouter()

@router.delete("/admin/delete_user")
def delete_user(admin_id: str = Query(...), target_user_id: str = Query(...)):
    if not admin_handler.is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    success, message = admin_handler.delete_user(target_user_id)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}

@router.get("/admin/users")
def get_all_users(admin_id: str = Query(...)):
    if not admin_handler.is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    details = admin_handler.get_all_users_details()
    return {"users": details}



class RoleCreateRequest(BaseModel):
    role_name: str
    role_level: int

@router.post("/admin/add_role")
def add_role(role: RoleCreateRequest, admin_id: str = Query(...)):
    if not admin_handler.is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    success, message = admin_handler.add_role(role.role_name, role.role_level)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@router.delete("/admin/delete_role")
def delete_role(role_name: str = Query(...), admin_id: str = Query(...)):
    if not admin_handler.is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    success, message = admin_handler.delete_role(role_name)
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}


@router.get("/admin/roles")
def get_all_roles(admin_id: str = Query(...)):
    if not admin_handler.is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    roles = admin_handler.get_all_roles()
    return {"roles": roles}