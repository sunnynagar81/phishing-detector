from fastapi import APIRouter, HTTPException

from app.db import save_scan
from app.ml.predict import predict_url
from app.schemas import ScanResponse, URLRequest

router = APIRouter(prefix="/api/scan", tags=["scan"])


@router.post("/url", response_model=ScanResponse)
def scan_url(req: URLRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="URL is empty")

    result = predict_url(req.url)

    # Saving history must never break scanning
    try:
        save_scan("url", req.url, result["status"], result["phishing_probability"], result["reasons"])
    except Exception as e:
        print("Could not save scan:", e)

    return result