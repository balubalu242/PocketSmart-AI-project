from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth import optional_user, require_user
from app.database import list_history, get_recommendation

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def context(request: Request, **extra):
    return {"request": request, "user": optional_user(request), **extra}


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse(request, "index.html", context(request))


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", context(request))


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", context(request))


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(require_user)):
    recent = list_history(user["id"], 5)
    return templates.TemplateResponse(
        request, "dashboard.html", context(request, recent=recent)
    )


@router.get("/planner/home", response_class=HTMLResponse)
def home_planner(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse(request, "home_planner.html", context(request))


@router.get("/planner/party", response_class=HTMLResponse)
def party_planner(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse(request, "party_planner.html", context(request))


@router.get("/planner/jewelry", response_class=HTMLResponse)
def jewelry_planner(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse(request, "jewelry_planner.html", context(request))


@router.get("/history-view", response_class=HTMLResponse)
def history_page(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse(
        request, "history.html", context(request, history=list_history(user["id"]))
    )


@router.get("/recommendations/{recommendation_id}", response_class=HTMLResponse)
def recommendation_page(
    request: Request,
    recommendation_id: int,
    user=Depends(require_user),
):
    item = get_recommendation(user["id"], recommendation_id)
    if not item:
        from fastapi import HTTPException
        raise HTTPException(404, "Recommendation not found.")
    return templates.TemplateResponse(
        request, "recommendations.html", context(request, item=item)
    )
