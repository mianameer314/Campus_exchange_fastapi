# Campus Exchange API - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Tech Stack](#architecture--tech-stack)
3. [Environment Setup](#environment-setup)
4. [API Endpoints](#api-endpoints)
5. [Testing Guide](#testing-guide)
6. [Integration Guide](#integration-guide)
7. [Code Examples](#code-examples)

## Project Overview

Campus Exchange is a comprehensive marketplace API built with FastAPI for university students to buy, sell, and exchange items within their campus community. The system includes advanced features like AI-powered price suggestions, real-time chat, and intelligent search capabilities.

### Key Features
- **Authentication & Authorization**: JWT-based auth with university email validation
- **Marketplace CRUD**: Complete listing management with image uploads
- **Advanced Search**: PostgreSQL full-text search with filters and pagination
- **AI Integration**: Price suggestions, duplicate detection, and recommendations
- **Real-time Chat**: WebSocket-based messaging system
- **Admin Panel**: Comprehensive administrative controls
- **File Storage**: Support for both local and S3 cloud storage
- **Email System**: Verification emails and notifications

## Architecture & Tech Stack

### Backend Framework
\`\`\`python
# FastAPI with async support
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Campus Exchange API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
\`\`\`

### Database Layer
\`\`\`python
# SQLAlchemy with PostgreSQL
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Models Example
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    university = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
\`\`\`

### Security Implementation
\`\`\`python
# JWT Authentication
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: str) -> str:
    to_encode = {"sub": data}
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
\`\`\`

## Environment Setup

### Required Environment Variables
\`\`\`bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/campus_exchange

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Admin Account
ADMIN_EMAIL=admin@cuiatk.edu.pk
ADMIN_PASSWORD=secure-admin-password

# Email Configuration (Gmail SMTP)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@campusexchange.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# University Email Domains
ALLOWED_EMAIL_DOMAINS=cuiatk.edu.pk,uni.edu,college.edu

# Storage Configuration
STORAGE_BACKEND=LOCAL  # or S3
UPLOAD_DIR=./uploads

# AWS S3 (if using S3 storage)
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key

# AI Service Configuration
AI_API_KEY=your-openai-api-key
AI_MODEL=gpt-4o-mini
AI_PRICE_SUGGEST_ENABLED=true
AI_DUPLICATE_CHECK_ENABLED=true
AI_RECOMMEND_ENABLED=true

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://yourfrontend.com
\`\`\`

### Installation & Setup
\`\`\`bash
# 1. Clone and setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup database
alembic upgrade head

# 4. Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

## API Endpoints

### 1. Authentication Endpoints

#### Sign Up
\`\`\`http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "student@cuiatk.edu.pk",
  "password": "securepassword123"
}
\`\`\`

**Response:**
\`\`\`json
{
  "message": "Registration successful. Please login to get your token."
}
\`\`\`

#### Login
\`\`\`http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "student@cuiatk.edu.pk",
  "password": "securepassword123"
}
\`\`\`

**Response:**
\`\`\`json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
\`\`\`

#### Get Current User
\`\`\`http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
\`\`\`

**Response:**
\`\`\`json
{
  "id": 1,
  "email": "student@cuiatk.edu.pk",
  "is_admin": false,
  "is_verified": true,
  "university_name": "COMSATS Attock University"
}
\`\`\`

### 2. Listings Management

#### Create Listing
\`\`\`http
POST /api/v1/listings
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

title: "MacBook Pro 2021 for Sale"
description: "13-inch MacBook Pro with M1 chip, excellent condition"
category: "Electronics"
price: 1200.00
images: [file1.jpg, file2.jpg]
\`\`\`

**Response:**
\`\`\`json
{
  "id": 1,
  "title": "MacBook Pro 2021 for Sale",
  "description": "13-inch MacBook Pro with M1 chip, excellent condition",
  "category": "Electronics",
  "price": 1200.0,
  "images": [
    "/uploads/listings/uuid-filename1.jpg",
    "/uploads/listings/uuid-filename2.jpg"
  ],
  "status": "ACTIVE",
  "owner_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
\`\`\`

#### Search Listings
\`\`\`http
GET /api/v1/listings/search?q=laptop&category=Electronics&min_price=500&max_price=2000&page=1&page_size=10
\`\`\`

**Response:**
\`\`\`json
{
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false,
  "results": [
    {
      "id": 1,
      "title": "MacBook Pro 2021 for Sale",
      "category": "Electronics",
      "price": 1200.0,
      "images": ["/uploads/listings/uuid-filename.jpg"],
      "status": "ACTIVE",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
\`\`\`

### 3. AI Services

#### Price Suggestion
\`\`\`http
POST /api/v1/ai/price-suggest
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "MacBook Pro 2021",
  "description": "13-inch MacBook Pro with M1 chip, 8GB RAM, 256GB SSD",
  "category": "Electronics",
  "condition": "Used - Good"
}
\`\`\`

**Response:**
\`\`\`json
{
  "suggested_price": 1150.0,
  "confidence": 0.85,
  "price_range": {
    "min": 1000.0,
    "max": 1300.0
  },
  "reasoning": "Based on current market prices for similar MacBook Pro models with M1 chip in good condition"
}
\`\`\`

#### Duplicate Detection
\`\`\`http
POST /api/v1/ai/duplicate-check
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "MacBook Pro for Sale",
  "description": "Selling my MacBook Pro laptop",
  "category": "Electronics"
}
\`\`\`

**Response:**
\`\`\`json
{
  "is_duplicate": true,
  "confidence": 0.92,
  "similar_listings": [
    {
      "id": 5,
      "title": "MacBook Pro 2021 for Sale",
      "similarity_score": 0.89
    }
  ],
  "recommendation": "Consider checking existing similar listings before posting"
}
\`\`\`

### 4. Advanced Search Features

#### Advanced Search with Multiple Filters
\`\`\`http
GET /api/v1/listings/advanced-search?keywords=laptop,computer&categories=Electronics&price_ranges=500-1000,1000-2000&universities=COMSATS&exclude_sold=true
\`\`\`

#### Search Suggestions
\`\`\`http
GET /api/v1/listings/suggestions?q=lap&limit=5
\`\`\`

**Response:**
\`\`\`json
{
  "suggestions": [
    "laptop",
    "laptop bag",
    "laptop stand",
    "laptop charger",
    "laptop case"
  ]
}
\`\`\`

## Testing Guide

### Sequential Testing Workflow

#### Phase 1: System Health Check
\`\`\`bash
# 1. Test basic connectivity
curl http://localhost:8000/

# 2. Check health endpoints
curl http://localhost:8000/healthz
curl http://localhost:8000/health/detailed
\`\`\`

#### Phase 2: Authentication Flow
\`\`\`bash
# 1. Sign up new user
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@cuiatk.edu.pk","password":"testpass123"}'

# 2. Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@cuiatk.edu.pk","password":"testpass123"}' \
  | jq -r '.access_token')

# 3. Verify authentication
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/me
\`\`\`

#### Phase 3: Core Functionality
\`\`\`bash
# 1. Create a listing
LISTING_ID=$(curl -X POST http://localhost:8000/api/v1/listings \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Test Laptop" \
  -F "description=Great laptop for sale" \
  -F "category=Electronics" \
  -F "price=500.00" \
  | jq -r '.id')

# 2. Search for listings
curl "http://localhost:8000/api/v1/listings/search?q=laptop&page=1&page_size=5"

# 3. Test AI services
curl -X POST http://localhost:8000/api/v1/ai/price-suggest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"MacBook Pro","description":"Good condition","category":"Electronics","condition":"Used"}'
\`\`\`

### Postman Testing Sequence

1. **Import Collection**: Import the `postman_collection.json` file
2. **Set Variables**: Configure base_url, user_email, user_password
3. **Run Authentication**: Execute signup → login → get current user
4. **Test Core Features**: Create listing → search → update → delete
5. **Test AI Services**: Price suggest → duplicate check → recommendations
6. **Test Admin Features**: Admin login → user management → listing moderation

### Automated Testing Script
\`\`\`python
# test_api.py
import requests
import json

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def test_auth_flow(self):
        # Sign up
        signup_data = {
            "email": "test@cuiatk.edu.pk",
            "password": "testpass123"
        }
        response = requests.post(f"{self.base_url}/api/v1/auth/signup", json=signup_data)
        assert response.status_code == 200
        
        # Login
        response = requests.post(f"{self.base_url}/api/v1/auth/login", json=signup_data)
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        print("✅ Authentication flow test passed")
    
    def test_listing_crud(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create listing
        listing_data = {
            "title": "Test Item",
            "description": "Test description",
            "category": "Electronics",
            "price": "100.00"
        }
        response = requests.post(f"{self.base_url}/api/v1/listings", 
                               headers=headers, data=listing_data)
        assert response.status_code == 200
        listing_id = response.json()["id"]
        
        # Get listing
        response = requests.get(f"{self.base_url}/api/v1/listings/{listing_id}")
        assert response.status_code == 200
        
        print("✅ Listing CRUD test passed")
    
    def run_all_tests(self):
        self.test_auth_flow()
        self.test_listing_crud()
        print("🎉 All tests passed!")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
\`\`\`

## Integration Guide

### Frontend Integration (React/Next.js)

#### API Client Setup
\`\`\`javascript
// api/client.js
class CampusExchangeAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }

  // Authentication methods
  async login(email, password) {
    const response = await this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  async getCurrentUser() {
    return this.request('/api/v1/auth/me');
  }

  // Listing methods
  async searchListings(params) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/v1/listings/search?${queryString}`);
  }

  async createListing(formData) {
    return this.request('/api/v1/listings', {
      method: 'POST',
      headers: {}, // Remove Content-Type for FormData
      body: formData,
    });
  }

  // AI methods
  async getPriceSuggestion(listingData) {
    return this.request('/api/v1/ai/price-suggest', {
      method: 'POST',
      body: JSON.stringify(listingData),
    });
  }
}

export default new CampusExchangeAPI();
\`\`\`

#### React Hook Example
\`\`\`javascript
// hooks/useListings.js
import { useState, useEffect } from 'react';
import api from '../api/client';

export function useListings(searchParams = {}) {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchListings = async () => {
      try {
        setLoading(true);
        const response = await api.searchListings(searchParams);
        setListings(response.results);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchListings();
  }, [JSON.stringify(searchParams)]);

  return { listings, loading, error };
}
\`\`\`

### ML Integration (Python)

#### Custom ML Model Integration
\`\`\`python
# ml_integration.py
import joblib
import numpy as np
from typing import Dict, List
from app.services.ai_service import AIService

class CustomMLService(AIService):
    def __init__(self):
        # Load your trained models
        self.price_model = joblib.load('models/price_prediction_model.pkl')
        self.duplicate_model = joblib.load('models/duplicate_detection_model.pkl')
        self.recommendation_model = joblib.load('models/recommendation_model.pkl')
    
    async def suggest_price(self, title: str, description: str, 
                          category: str, condition: str) -> Dict:
        # Feature extraction
        features = self.extract_features(title, description, category, condition)
        
        # Predict price
        predicted_price = self.price_model.predict([features])[0]
        confidence = self.price_model.predict_proba([features]).max()
        
        return {
            "suggested_price": float(predicted_price),
            "confidence": float(confidence),
            "price_range": {
                "min": float(predicted_price * 0.8),
                "max": float(predicted_price * 1.2)
            },
            "reasoning": f"Based on {category} category analysis and condition assessment"
        }
    
    def extract_features(self, title: str, description: str, 
                        category: str, condition: str) -> List[float]:
        # Implement your feature extraction logic
        # This is a simplified example
        features = [
            len(title.split()),  # Title word count
            len(description.split()),  # Description word count
            self.category_encoder.transform([category])[0],  # Category encoding
            self.condition_encoder.transform([condition])[0],  # Condition encoding
        ]
        return features

# Replace the AI service in your FastAPI app
# In main.py or wherever you initialize services
from ml_integration import CustomMLService
ai_service = CustomMLService()
\`\`\`

### Mobile App Integration (React Native)

#### API Service for Mobile
\`\`\`javascript
// services/ApiService.js
import AsyncStorage from '@react-native-async-storage/async-storage';

class ApiService {
  constructor() {
    this.baseURL = 'https://your-api-domain.com';
  }

  async getToken() {
    return await AsyncStorage.getItem('access_token');
  }

  async setToken(token) {
    await AsyncStorage.setItem('access_token', token);
  }

  async authenticatedRequest(endpoint, options = {}) {
    const token = await this.getToken();
    
    return fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
  }

  async uploadListing(listingData, images) {
    const formData = new FormData();
    
    // Add text fields
    Object.keys(listingData).forEach(key => {
      formData.append(key, listingData[key]);
    });
    
    // Add images
    images.forEach((image, index) => {
      formData.append('images', {
        uri: image.uri,
        type: image.type,
        name: `image_${index}.jpg`,
      });
    });

    const token = await this.getToken();
    
    return fetch(`${this.baseURL}/api/v1/listings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });
  }
}

export default new ApiService();
\`\`\`

## Code Examples

### Database Models Deep Dive

#### User Model with Relationships
\`\`\`python
# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    university = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    listings = relationship("Listing", back_populates="owner", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "university": self.university,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
\`\`\`

#### Advanced Listing Model with Search
\`\`\`python
# models/listing.py
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum, ARRAY
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum

class ListingStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    ARCHIVED = "ARCHIVED"
    PENDING = "PENDING"

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    
    # Media and metadata
    images = Column(ARRAY(String), default=[])
    tags = Column(ARRAY(String), default=[])
    condition = Column(String, nullable=True)  # New, Used, Refurbished
    
    # Status and ownership
    status = Column(Enum(ListingStatus), default=ListingStatus.ACTIVE, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Location and contact
    location = Column(String, nullable=True)
    contact_method = Column(String, default="chat")  # chat, email, phone
    
    # Analytics
    view_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    
    # Search optimization
    search_vector = Column(TSVECTOR)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="listings")
    favorites = relationship("Favorite", back_populates="listing", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="listing", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "images": self.images,
            "status": self.status.value,
            "owner_id": self.owner_id,
            "view_count": self.view_count,
            "favorite_count": self.favorite_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
\`\`\`

### Advanced API Patterns

#### Dependency Injection for Database and Auth
\`\`\`python
# api/deps.py
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

security = HTTPBearer()

def get_db() -> Generator:
    """Database dependency"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must be verified"
        )
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
\`\`\`

#### Advanced Error Handling
\`\`\`python
# core/exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class CampusExchangeException(Exception):
    """Base exception for Campus Exchange"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserNotVerifiedException(CampusExchangeException):
    def __init__(self):
        super().__init__("User must be verified to perform this action", 403)

class ListingNotFoundException(CampusExchangeException):
    def __init__(self, listing_id: int):
        super().__init__(f"Listing with id {listing_id} not found", 404)

class UnauthorizedListingAccessException(CampusExchangeException):
    def __init__(self):
        super().__init__("You don't have permission to access this listing", 403)

async def campus_exchange_exception_handler(request: Request, exc: CampusExchangeException):
    logger.error(f"Campus Exchange Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": "campus_exchange_error"}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "type": "validation_error"
        }
    )
\`\`\`

This comprehensive documentation provides everything needed to understand, test, and integrate with your Campus Exchange API. The system is production-ready with robust error handling, security measures, and scalable architecture patterns.
