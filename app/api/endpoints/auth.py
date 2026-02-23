from fastapi import APIRouter,Form,File,Body
auth_router = APIRouter()

@auth_router.post("/signup")
def auth_signup(
    q:str,
    name:str = Form(...),
    # email:str = Form(...),
    # image:File = File(...),
    ):

    return {
        "status":"ok signup",
        "name":name,
        "search":q

    }
@auth_router.post("/login")
def auth_login(data = Body(...)):
    return {
        "status":data,
        
    }