from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints.v1 import chat
from app.services.db_service import db

app = FastAPI(title="Tech Ecosystem GraphRAG API")

# Allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

@app.on_event("startup")
async def startup_event():
    db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Tech Ecosystem GraphRAG API"}

@app.get("/api/v1/ping")
def ping():
    return {"status": "ok", "message": "Connected to backend"}
