"""
Database Schemas

Pydantic models representing MongoDB collections. Class name lowercased = collection name.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    bio: Optional[str] = Field(None, description="Short bio")
    is_verified: bool = Field(False, description="Whether the user is verified")

class Listing(BaseModel):
    title: str = Field(..., description="Listing title")
    description: str = Field(..., description="Detailed description")
    price_usd: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="Category")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    seller_email: EmailStr = Field(..., description="Owner (user email)")
    cover_image: Optional[str] = Field(None, description="Image URL")
    rating: float = Field(4.8, ge=0, le=5, description="Average rating")
    sales: int = Field(0, ge=0, description="Number of sales")

class Order(BaseModel):
    buyer_email: EmailStr = Field(..., description="Buyer email")
    listing_id: str = Field(..., description="Purchased listing id")
    amount_usd: float = Field(..., ge=0, description="Paid amount")
    status: str = Field("paid", description="Order status")

class Submission(BaseModel):
    submitter_email: EmailStr = Field(..., description="Submitter email")
    title: str = Field(...)
    details: str = Field(...)
    category: str = Field(...)
    attachment_url: Optional[str] = None

# Lightweight activity log for dashboards
class Activity(BaseModel):
    actor_email: EmailStr
    action: str
    target: Optional[str] = None
    at: Optional[datetime] = None
