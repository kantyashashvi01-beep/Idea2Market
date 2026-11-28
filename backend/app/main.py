import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.db import SessionLocal
from app.models.models import Job
from app.api import health, auth, projects, jobs, facilities, admin

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("idea2market")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Idea2market API in env=%s", settings.ENV)
    logger.info("CORS origins allowed: %s", settings.cors_origin_list)

    # Recover any stale jobs left in running status on restart
    db = SessionLocal()
    try:
        ten_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        stale_jobs = db.query(Job).filter(Job.status == "running", Job.created_at < ten_minutes_ago).all()
        for j in stale_jobs:
            j.status = "failed"
            j.error_message = "Worker restarted or job timed out."
        if stale_jobs:
            db.commit()
            logger.info("Recovered %d stale running jobs.", len(stale_jobs))
    except Exception as e:
        logger.warning("Could not perform stale job recovery on startup: %s", str(e))
    finally:
        db.close()
    yield


app = FastAPI(
    title="Idea2market API",
    description="AI-Assisted Idea-to-Prototype Planning for Hardware Non-Engineers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Invalid request parameters.",
                "details": exc.errors(),
            }
        },
    )


# Include API Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(jobs.router)
app.include_router(facilities.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Idea2market API",
        "docs": "/docs",
        "health": "/health",
    }
