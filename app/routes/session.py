from fastapi import APIRouter, Depends

from app.auth import require_user
from app.database import list_history

router = APIRouter()


@router.get("/session-info")
def session_info(user=Depends(require_user)):
    return {
        "authenticated": True,
        "user_id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
    }


@router.get("/session-data")
def session_data(user=Depends(require_user)):
    history = list_history(user["id"], limit=10)
    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
        },
        "recent_recommendations": history,
    }


@router.get("/history")
def history(user=Depends(require_user)):
    return {"items": list_history(user["id"])}


@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id: int, user=Depends(require_user)):
    from app.database import get_recommendation
    item = get_recommendation(user["id"], recommendation_id)
    if not item:
        from fastapi import HTTPException
        raise HTTPException(404, "Recommendation not found.")
    return item
