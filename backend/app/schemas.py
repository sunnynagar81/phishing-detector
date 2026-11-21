from typing import List

from pydantic import BaseModel


class URLRequest(BaseModel):
    url: str


class Explanation(BaseModel):
    feature: str
    value: float
    impact: float


class ScanResponse(BaseModel):
    url: str
    status: str
    phishing_probability: float
    reasons: List[str]
    explanation: List[Explanation] = []
    
class TextRequest(BaseModel):
    text: str
    subject: str = ""


class FlaggedURL(BaseModel):
    url: str
    status: str
    probability: float


class TextScanResponse(BaseModel):
    status: str
    phishing_probability: float
    reasons: List[str]
    explanation: List[Explanation] = []
    flagged_urls: List[FlaggedURL] = []    