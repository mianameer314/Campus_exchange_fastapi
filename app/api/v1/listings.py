import uuid
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api import deps
from app.core.config import settings
from app.models.listing import Listing
from app.models.user import User
from app.schemas.listing import ListingOut, ListingUpdate, ListingStatusPatch
from app.utils.storage import (
    save_upload,
    gen_object_key,
    public_url_for_key,
    get_s3_client,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/listings", tags=["Listings"])


# -------- Create listing (LOCAL or S3 based on settings) --------
@router.post("", response_model=ListingOut)
async def create_listing(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: Decimal = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
):
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified")

    urls = []

    if settings.STORAGE_BACKEND == "LOCAL":
        # Save files locally
        for f in images or []:
            url = save_upload(f, subdir="listings")
            urls.append(url)
    elif settings.STORAGE_BACKEND == "S3":
        # Upload files to S3 directly
        s3_client = get_s3_client()
        for f in images or []:
            key = gen_object_key("listings", f.filename)
            s3_client.upload_fileobj(f.file, settings.S3_BUCKET, key)
            urls.append(public_url_for_key(key))
    else:
        raise HTTPException(status_code=500, detail="Invalid storage backend")

    obj = Listing(
        title=title,
        description=description,
        category=category,
        price=float(price),
        images=urls,
        owner_id=user.id,
        status="ACTIVE",
    )
    
    search_text = f"{title} {description} {category}"
    obj.search_vector = func.to_tsvector('english', search_text)
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    
    NotificationService.notify_listing_created(db, obj, user.id)
    
    return obj


# -------- Get listing --------
@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(deps.get_db)):
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    return obj


# -------- Update listing --------
@router.patch("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
):
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    if obj.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified")

    update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
    
    # Additional validation to prevent updating with empty/default values
    filtered_update_data = {}
    for field, value in update_data.items():
        # Skip empty strings and empty lists (preserve existing values)
        if field == "title" and value and value.strip():
            filtered_update_data[field] = value.strip()
        elif field == "description" and value and value.strip():
            filtered_update_data[field] = value.strip()
        elif field == "category" and value and value.strip():
            filtered_update_data[field] = value.strip()
        elif field == "price" and value is not None and value > 0:
            filtered_update_data[field] = float(value)
        elif field == "images" and value is not None:
            # Only update images if explicitly provided and not empty
            filtered_update_data[field] = value
    
    # Apply only the filtered updates
    for field, value in filtered_update_data.items():
        setattr(obj, field, value)

    if any(field in filtered_update_data for field in ['title', 'description', 'category']):
        search_text = f"{obj.title} {obj.description} {obj.category}"
        obj.search_vector = func.to_tsvector('english', search_text)

    db.commit()
    db.refresh(obj)
    
    if filtered_update_data:  # Only notify if something was actually updated
        NotificationService.notify_listing_updated(db, obj, user.id)
    
    return obj


# -------- Patch status --------
@router.patch("/{listing_id}/status", response_model=ListingOut)
def patch_status(
    listing_id: int,
    payload: ListingStatusPatch,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
):
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    if obj.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    if payload.status not in {"ACTIVE", "SOLD", "ARCHIVED"}:
        raise HTTPException(status_code=422, detail="Invalid status")

    obj.status = payload.status
    db.commit()
    db.refresh(obj)
    return obj


# -------- Delete listing --------
@router.delete("/{listing_id}", status_code=204)
def delete_listing(
    listing_id: int,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
):
    obj = db.query(Listing).filter(Listing.id == listing_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Listing not found")
    if obj.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified")

    db.delete(obj)
    db.commit()
