from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ResearchMate AI API",
    description="Backend API for the ResearchMate AI project",
    version="1.0.0"
)

# Allow the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to ResearchMate AI API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "ResearchMate AI backend is running"
    }