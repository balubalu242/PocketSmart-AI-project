from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import require_user
from app.config import get_settings
from app.database import save_recommendation
from app.models.schemas import HomeRequest, JewelryRequest, PartyRequest, RecommendationResponse
from app.services.planner_service import generate_home, generate_jewelry, generate_party

router = APIRouter()


def save_result(user: dict, planner: str, request_data: dict, result: RecommendationResponse):
    result_data = result.model_dump()
    recommendation_id = save_recommendation(user["id"], planner, request_data, result_data)
    return {"id": recommendation_id, **result_data}


@router.post("/generate-home")
def generate_home_route(payload: HomeRequest, user=Depends(require_user)):
    result = generate_home(payload)
    return save_result(user, "home", payload.model_dump(), result)


@router.post("/generate-party")
def generate_party_route(payload: PartyRequest, user=Depends(require_user)):
    result = generate_party(payload)
    return save_result(user, "party", payload.model_dump(), result)


@router.post("/generate-jewelry")
async def generate_jewelry_route(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form("elegant"),
    metal_preference: str = Form("any"),
    notes: str = Form(""),
    image: UploadFile | None = File(None),
    user=Depends(require_user),
):
    payload = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        metal_preference=metal_preference,
        notes=notes,
    )

    image_bytes = None
    image_mime = None
    if image:
        settings = get_settings()
        allowed = {"image/jpeg", "image/png", "image/webp"}
        if image.content_type not in allowed:
            raise HTTPException(400, "Only JPEG, PNG, or WEBP images are supported.")

        data = await image.read()
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(413, "Image is too large.")

        image_bytes = data
        image_mime = image.content_type

    result = generate_jewelry(payload, image_bytes, image_mime)
    return save_result(
        user,
        "jewelry",
        {**payload.model_dump(), "image_supplied": bool(image_bytes)},
        result,
    )
