from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.routes.paper_routes import router as paper_router
from app.routes.document_routes import router as document_router
from app.services.exceptions import ResearchMateException
from app.routes.library_routes import router as library_router

from app.services.error_handlers import (
    researchmate_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

from app.routes.paper_routes import router as paper_router


app = FastAPI(
    title="ResearchMate AI",
    description="Intelligent Academic Research Assistant",
    version="1.0.0"
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