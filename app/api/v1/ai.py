from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.api.deps import get_db, get_current_user
from app.models.listing import Listing
from app.schemas.ai import (
    PriceSuggestRequest, PriceSuggestResponse,
    DuplicateCheckRequest, DuplicateCheckResponse,
    RecommendRequest, RecommendResponse
)
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/price-suggest", response_model=PriceSuggestResponse)
async def suggest_price(
    request: PriceSuggestRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """AI-powered price suggestion for listings"""
    if not settings.AI_PRICE_SUGGEST_ENABLED:
        raise HTTPException(status_code=503, detail="Price suggestion service is disabled")
    
    try:
        result = await ai_service.suggest_price(
            title=request.title,
            description=request.description,
            category=request.category,
            condition=request.condition
        )
        return PriceSuggestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/duplicate-check", response_model=DuplicateCheckResponse)
async def check_duplicate(
    request: DuplicateCheckRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """AI-powered duplicate listing detection"""
    if not settings.AI_DUPLICATE_CHECK_ENABLED:
        raise HTTPException(status_code=503, detail="Duplicate check service is disabled")
    
    # Get recent listings for comparison
    recent_listings = db.query(Listing).filter(
        Listing.category == request.category
    ).order_by(Listing.created_at.desc()).limit(20).all()
    
    existing_listings = [
        {
            "id": listing.id,
            "title": listing.title,
            "description": listing.description or ""
        }
        for listing in recent_listings
    ]
    
    try:
        result = await ai_service.check_duplicate(
            title=request.title,
            description=request.description,
            existing_listings=existing_listings
        )
        return DuplicateCheckResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/recommend", response_model=RecommendResponse)
async def recommend_listings(
    request: RecommendRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """AI-powered listing recommendations"""
    if not settings.AI_RECOMMEND_ENABLED:
        raise HTTPException(status_code=503, detail="Recommendation service is disabled")
    
    # Get available listings
    available_listings = db.query(Listing).filter(
        Listing.status == "ACTIVE"
    ).order_by(Listing.created_at.desc()).limit(50).all()
    
    listings_data = [
        {
            "id": listing.id,
            "title": listing.title,
            "category": listing.category,
            "price": float(listing.price)
        }
        for listing in available_listings
    ]
    
    try:
        result = await ai_service.recommend_listings(
            user_preferences=request.user_preferences,
            available_listings=listings_data
        )
        return RecommendResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.get("/health")
async def ai_health_check():
    """Check AI service health and configuration"""
    return {
        "price_suggest_enabled": settings.AI_PRICE_SUGGEST_ENABLED,
        "duplicate_check_enabled": settings.AI_DUPLICATE_CHECK_ENABLED,
        "recommend_enabled": settings.AI_RECOMMEND_ENABLED,
        "ai_service_configured": bool(settings.AI_API_KEY),
        "model": settings.AI_MODEL
    }
