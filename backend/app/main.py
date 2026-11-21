import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routes import history, text, url

app = FastAPI(title="Phishing Detection API")

# Extra origins (your Vercel URL) come from the ALLOWED_ORIGINS environment variable
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
origins += [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(url.router)
app.include_router(text.router)
app.include_router(history.router)


@app.on_event("startup")
def startup():
    try:
        init_db()
    except Exception as e:
        print("MongoDB not reachable, history disabled:", e)


@app.get("/")
def health():
    return {"status": "ok"}