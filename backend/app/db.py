import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import DESCENDING, MongoClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "phishing_db")

# Short timeout so a stopped MongoDB gives a quick error instead of hanging
client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=3000, tz_aware=True)
db = client[MONGODB_DB]
scans = db["scans"]


def init_db():
    scans.create_index([("created_at", DESCENDING)])
    scans.create_index("status")
    scans.create_index("scan_type")


def save_scan(scan_type: str, content: str, status: str, probability: float, reasons: list):
    scans.insert_one({
        "scan_type": scan_type,  # url / email / sms
        "content": content,
        "status": status,  # safe / suspicious / dangerous
        "probability": probability,
        "reasons": reasons,
        "created_at": datetime.now(timezone.utc),
    })