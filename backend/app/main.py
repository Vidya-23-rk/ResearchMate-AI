from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.routes.paper_routes import router as paper_router
from app.routes.document_routes import router as document_router
from app.routes.library_routes import router as library_router
from app.services.exceptions import ResearchMateException
from app.services.error_handlers import (
    researchmate_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.database.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="ResearchMate AI",
    description="Intelligent Academic Research Assistant",
    version="1.0.0",
    lifespan=lifespan
)


# ---------------------------------------
# CORS — allow the React frontend
# ---------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ---------------------------------------
# Exception handlers
# ---------------------------------------

app.add_exception_handler(
    ResearchMateException,
    researchmate_exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    Exception,
    generic_exception_handler
)


# ---------------------------------------
# Routes
# ---------------------------------------

app.include_router(paper_router)
app.include_router(document_router)
app.include_router(library_router)


@app.get("/")
def root():
    return {
        "message": "ResearchMate AI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }