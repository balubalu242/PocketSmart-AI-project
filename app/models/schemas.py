from typing import Literal

from pydantic import BaseModel, Field, field_validator


PlannerType = Literal["home", "party", "jewelry"]


class RoomInput(BaseModel):
    room_type: str = Field(min_length=2, max_length=50)
    quantity: int = Field(default=1, ge=1, le=20)
    items: list[str] = Field(default_factory=list, max_length=20)


class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    rooms: list[RoomInput] = Field(min_length=1, max_length=10)
    style: str = Field(default="modern", min_length=2, max_length=50)
    city: str = Field(default="Chennai", min_length=2, max_length=80)
    notes: str = Field(default="", max_length=500)


class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guest_count: int = Field(ge=1, le=10_000)
    event_type: str = Field(min_length=2, max_length=60)
    venue: str = Field(default="home", min_length=2, max_length=120)
    city: str = Field(default="Chennai", min_length=2, max_length=80)
    food_preference: str = Field(default="mixed", min_length=2, max_length=60)
    notes: str = Field(default="", max_length=500)


class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=80)
    style: str = Field(default="elegant", min_length=2, max_length=60)
    metal_preference: str = Field(default="any", min_length=2, max_length=60)
    notes: str = Field(default="", max_length=500)


class RecommendationItem(BaseModel):
    name: str
    category: str
    platform: str
    estimated_price: float = Field(ge=0)
    why: str
    url: str = ""
    tags: list[str] = Field(default_factory=list)


class BudgetAllocation(BaseModel):
    category: str
    amount: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    explanation: str


class RecommendationResponse(BaseModel):
    planner: PlannerType
    title: str
    summary: str
    budget: float
    allocated_total: float
    allocations: list[BudgetAllocation]
    recommendations: list[RecommendationItem]
    tips: list[str] = Field(default_factory=list)
    disclaimer: str = "Prices and availability are estimates. Verify details with the provider before purchase."
    source: str = "fallback"
