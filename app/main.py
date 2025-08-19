import logging
import sys
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, LoggingMiddleware
from app.api.v1 import auth, reports, verification, listings, search, favorites, notifications, admin, ai, chat
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log') if settings.ENV == 'production' else logging.StreamHandler()
    ]
)

log = logging.getLogger("uvicorn.error")

app = FastAPI(
    title=settings.APP_NAME, 
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)


# root
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the campus_exchange API"}

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

if settings.ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*.vercel.app", "*.railway.app", "localhost"]
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.on_event("startup")
def create_single_admin():
    print("DEBUG: Entering create_single_admin startup event.") # Debug print
    try:
        with SessionLocal() as db:
            print("DEBUG: SessionLocal created.") # Debug print
            admin = db.query(User).filter(User.is_admin == True).first()
            if not admin:
                print("DEBUG: Admin user not found. Attempting creation.") # Debug print
                admin_username = settings.ADMIN_EMAIL.split("@")[0].lower()
                new_admin = User(
                    id=admin_username,  # Added missing id field
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hash_password(settings.ADMIN_PASSWORD),
                    is_admin=True,
                    is_verified=True,
                )
                db.add(new_admin)
                db.commit()
                db.refresh(new_admin) # Refresh to get ID if needed, or if other properties are populated by DB
                log.info("Admin user created: %s", settings.ADMIN_EMAIL)
                print(f"DEBUG: Admin user created: {settings.ADMIN_EMAIL}") # Debug print
            else:
                log.info("Admin already exists, skipping creation")
                print("DEBUG: Admin already exists, skipping creation.") # Debug print
        print("DEBUG: Exiting create_single_admin successfully.") # Debug print
    except Exception as e:
        log.error("Admin bootstrap failed: %s", e, exc_info=True) # exc_info=True logs full traceback
        print(f"ERROR: Admin bootstrap failed: {e}") # Debug print
        import traceback
        traceback.print_exc(file=sys.stderr) # IMP: Force full traceback to stderr
        # Re-raising ensures the container truly exits with an error for Railway to potentially catch better
        raise e 

app.include_router(admin.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(listings.router, prefix="/api/v1")
app.include_router(favorites.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

@app.get("/healthz", tags=["Health"])
def health():
    return {"status": "ok"}

@app.get("/health/detailed", tags=["Health"])
async def detailed_health():
    """Detailed health check for monitoring"""
    try:
        # Test database connection
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENV,
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        log.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )
