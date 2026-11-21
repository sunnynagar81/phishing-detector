from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Query

from app.db import scans

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
def history(
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    scan_type: Optional[str] = None,
):
    q = {}
    if status:
        q["status"] = status
    if scan_type:
        q["scan_type"] = scan_type
    rows = scans.find(q).sort("created_at", -1).limit(limit)
    return [
        {
            "id": str(r["_id"]),
            "scan_type": r.get("scan_type"),
            "content": r.get("content"),
            "status": r.get("status"),
            "probability": r.get("probability"),
            "reasons": r.get("reasons", []),
            "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
        }
        for r in rows
    ]


@router.get("/stats")
def stats(days: int = Query(14, ge=1, le=90)):
    total = scans.count_documents({})
    by_status = {d["_id"]: d["n"] for d in scans.aggregate(
        [{"$group": {"_id": "$status", "n": {"$sum": 1}}}])}
    by_type = {d["_id"]: d["n"] for d in scans.aggregate(
        [{"$group": {"_id": "$scan_type", "n": {"$sum": 1}}}])}

    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = scans.aggregate([
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": {
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "status": "$status",
            },
            "n": {"$sum": 1},
        }},
        {"$sort": {"_id.date": 1}},
    ])
    daily = {}
    for r in rows:
        d, s = r["_id"]["date"], r["_id"]["status"]
        entry = daily.setdefault(d, {"date": d, "safe": 0, "suspicious": 0, "dangerous": 0})
        entry[s] = r["n"]

    return {
        "total": total,
        "safe": by_status.get("safe", 0),
        "suspicious": by_status.get("suspicious", 0),
        "dangerous": by_status.get("dangerous", 0),
        "by_type": by_type,
        "daily": list(daily.values()),
    }


@router.delete("/history")
def clear_history():
    result = scans.delete_many({})
    return {"deleted": result.deleted_count}