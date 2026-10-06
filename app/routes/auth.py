from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import create_access_token, hash_password, verify_password
from app.database import create_user, get_user_by_email

router = APIRouter()


@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
):
    email = email.strip().lower()
    full_name = full_name.strip()

    if len(full_name) < 2:
        raise HTTPException(400, "Full name is required.")
    if len(password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")
    if get_user_by_email(email):
        raise HTTPException(409, "An account with that email already exists.")

    user = create_user(email, hash_password(password), full_name)
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        "access_token",
        create_access_token(user["id"]),
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response


@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password.")

    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        "access_token",
        create_access_token(user["id"]),
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.post("/token")
def token(email: str = Form(...), password: str = Form(...)):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password.")
    return {"access_token": create_access_token(user["id"]), "token_type": "bearer"}
