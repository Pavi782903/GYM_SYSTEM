from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.database import engine
from backend.models.models import Base
from backend.routers import auth, classes, bookings

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gym Membership & Class Booking System", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(bookings.router)

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.get("/{page}")
def serve_page(page: str):
    import os
    path = f"frontend/{page}"
    if os.path.exists(path):
        return FileResponse(path)
    return FileResponse("frontend/index.html")
