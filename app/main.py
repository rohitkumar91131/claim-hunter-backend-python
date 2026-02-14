from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, analyze, history
from app.config import settings

app = FastAPI(title="Claim Hunter Backend")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    # In production, this MUST be a specific list of origins, e.g. ["http://localhost:3000"]
    # Credentials cannot be used with allow_origins=["*"] in some browsers, but FastAPI handles it mostly.
    # However, strict specs say exact origin is needed. For dev, we often use specific localhost.
    allow_origins=settings.BACKEND_CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
app.include_router(history.router, prefix="/history", tags=["History"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Claim Hunter Backend"}
