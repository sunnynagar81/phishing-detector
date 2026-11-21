from fastapi import APIRouter, HTTPException

from app.db import save_scan
from app.ml.predict_text import predict_email, predict_sms
from app.schemas import TextRequest, TextScanResponse

router = APIRouter(prefix="/api/scan", tags=["scan"])


def _save(kind: str, content: str, result: dict):
    try:
        save_scan(kind, content[:500], result["status"],
                  result["phishing_probability"], result["reasons"])
    except Exception as e:
        print("Could not save scan:", e)


@router.post("/sms", response_model=TextScanResponse)
def scan_sms(req: TextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Message is empty")
    result = predict_sms(req.text)
    _save("sms", req.text, result)
    return result


@router.post("/email", response_model=TextScanResponse)
def scan_email(req: TextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Email body is empty")
    result = predict_email(req.subject, req.text)
    _save("email", f"{req.subject} | {req.text}", result)
    return result