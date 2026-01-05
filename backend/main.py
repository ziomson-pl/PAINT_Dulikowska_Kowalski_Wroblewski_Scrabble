from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

from app.routes import auth, games, profile, chat

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scrabble Game API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(profile.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Scrabble Game API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
