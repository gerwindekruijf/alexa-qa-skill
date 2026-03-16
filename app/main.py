import os
import warnings

from cryptography.utils import CryptographyDeprecationWarning
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import alexa, health

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

production_url = os.getenv("API_GATEWAY_URL")
local_url = "http://localhost:80"

servers = [
    {"url": local_url, "description": "Local Docker"},
]

if production_url:
    servers.insert(0, {"url": production_url, "description": "AWS API Gateway"})

app = FastAPI(
    title="Alexa Skill",
    version="1.0.0",
    servers=servers,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
app.include_router(alexa.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {"status": "secure", "service": "Alexa Skill Backend"}
