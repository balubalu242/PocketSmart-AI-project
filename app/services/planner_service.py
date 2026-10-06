from typing import Any

from app.models.schemas import (
    BudgetAllocation,
    HomeRequest,
    JewelryRequest,
    PartyRequest,
    RecommendationItem,
    RecommendationResponse,
)
from app.services.catalog import catalog_for
from app.services.gemini_service import GeminiService


gemini = GeminiService()


def money(value: float) -> float:
    return round(float(value), 2)


def make_prompt(planner: str, payload: dict[str, Any], catalog: list[dict]) -> str:
    return f"""
You are PocketSmart AI, a budget-aware lifestyle planning assistant.

Planner: {planner}
User request:
{payload}

Available demo catalog:
{catalog}

Rules:
1. Stay within the user's stated budget.
2. Use the catalog items when possible; do not invent live prices or claim live availability.
3. Give practical category-level budget allocations.
4. Return concise explanations.
5. For jewelry, use the supplied image only as visual context if present. Do not identify the person.
6. The output must match the requested JSON schema exactly.
"""


def fallback_home(request: HomeRequest) -> RecommendationResponse:
    allocations = [
        BudgetAllocation(category="Furniture", amount=money(request.budget * .45), percentage=45, explanation="Prioritize the largest functional pieces."),
        BudgetAllocation(category="Lighting", amount=money(request.budget * .15), percentage=15, explanation="Keep lighting practical and style-consistent."),
        BudgetAllocation(category="Decor", amount=money(request.budget * .20), percentage=20, explanation="Use decor to reinforce the chosen style."),
        BudgetAllocation(category="Reserve", amount=money(request.budget * .20), percentage=20, explanation="Keep a reserve for delivery, installation and missing items."),
    ]
    items = [
        RecommendationItem(
            name=x["name"], category=x["category"], platform=x["platform"],
            estimated_price=x["estimated_price"], why=f"Fits a {request.style} home plan and is within the demo catalog.",
            url=x["url"], tags=x["tags"]
        )
        for x in catalog_for("home")[:5]
    ]
    return RecommendationResponse(
        planner="home",
        title="Budget-friendly home interior plan",
        summary=f"A {request.style} setup for {request.city}, planned around your budget.",
        budget=request.budget,
        allocated_total=request.budget,
        allocations=allocations,
        recommendations=items,
        tips=["Buy essential furniture first.", "Compare dimensions before ordering.", "Keep part of the budget for delivery and installation."],
    )


def fallback_party(request: PartyRequest) -> RecommendationResponse:
    allocations = [
        BudgetAllocation(category="Catering", amount=money(request.budget * .45), percentage=45, explanation="Food is usually the largest variable cost."),
        BudgetAllocation(category="Venue", amount=money(request.budget * .25), percentage=25, explanation="Keep venue cost controlled to protect the food budget."),
        BudgetAllocation(category="Decoration", amount=money(request.budget * .15), percentage=15, explanation="Use focused decorations around the main photo/entrance area."),
        BudgetAllocation(category="Reserve", amount=money(request.budget * .15), percentage=15, explanation="Reserve for last-minute needs."),
    ]
    items = []
    for x in catalog_for("party")[:5]:
        price = x["estimated_price"]
        if x["category"] == "catering":
            price *= request.guest_count
        items.append(
            RecommendationItem(
                name=x["name"], category=x["category"], platform=x["platform"],
                estimated_price=money(price),
                why=f"Suitable for a {request.event_type} event with {request.guest_count} guests.",
                url=x["url"], tags=x["tags"]
            )
        )
    return RecommendationResponse(
        planner="party",
        title=f"{request.event_type.title()} budget plan",
        summary=f"An event plan for {request.guest_count} guests in {request.city}.",
        budget=request.budget,
        allocated_total=request.budget,
        allocations=allocations,
        recommendations=items,
        tips=["Confirm per-person food pricing.", "Keep a written guest-count cutoff date.", "Reserve a contingency amount."],
    )


def fallback_jewelry(request: JewelryRequest, image_present: bool) -> RecommendationResponse:
    items = []
    for x in catalog_for("jewelry")[:5]:
        tags = set(x["tags"])
        relevance = request.style.lower() in tags or request.metal_preference.lower() in tags or request.occasion.lower() in tags
        if relevance or len(items) < 3:
            items.append(
                RecommendationItem(
                    name=x["name"], category=x["category"], platform=x["platform"],
                    estimated_price=x["estimated_price"],
                    why=f"Selected for a {request.style} look for a {request.occasion} occasion.",
                    url=x["url"], tags=x["tags"]
                )
            )
    return RecommendationResponse(
        planner="jewelry",
        title="Occasion-ready jewelry plan",
        summary=f"Jewelry suggestions for a {request.occasion} occasion with a {request.style} preference."
                + (" Outfit image was supplied for visual context." if image_present else ""),
        budget=request.budget,
        allocated_total=request.budget,
        allocations=[
            BudgetAllocation(category="Primary jewelry", amount=money(request.budget * .65), percentage=65, explanation="Main piece or coordinated set."),
            BudgetAllocation(category="Secondary pieces", amount=money(request.budget * .20), percentage=20, explanation="Add a small supporting piece if needed."),
            BudgetAllocation(category="Reserve", amount=money(request.budget * .15), percentage=15, explanation="Keep a reserve for price variation."),
        ],
        recommendations=items,
        tips=["Coordinate the scale of jewelry with the outfit.", "Check material descriptions before purchase.", "Treat online prices as estimates until verified."],
    )


def generate_home(request: HomeRequest) -> RecommendationResponse:
    fallback = fallback_home(request)
    result = gemini.generate(make_prompt("home", request.model_dump(), catalog_for("home")))
    return result or fallback


def generate_party(request: PartyRequest) -> RecommendationResponse:
    fallback = fallback_party(request)
    result = gemini.generate(make_prompt("party", request.model_dump(), catalog_for("party")))
    return result or fallback


def generate_jewelry(
    request: JewelryRequest,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
) -> RecommendationResponse:
    fallback = fallback_jewelry(request, bool(image_bytes))
    prompt = make_prompt(
        "jewelry",
        {**request.model_dump(), "outfit_image_supplied": bool(image_bytes)},
        catalog_for("jewelry"),
    )
    result = gemini.generate(prompt, image_bytes=image_bytes, image_mime=image_mime)
    return result or fallback
