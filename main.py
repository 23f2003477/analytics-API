
import os
from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

# Allow the assignment page to call our API from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY", "")
EMAIL = os.getenv("EMAIL", "23f2003477@ds.study.iitm.ac.in")


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: list[Event]


@app.post("/analytics")
def analytics(
    request: AnalyticsRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    # Reject requests with a missing or incorrect API key.
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    events = request.events
    user_totals = defaultdict(float)

    revenue = 0.0

    for event in events:
        if event.amount > 0:
            revenue += event.amount
            user_totals[event.user] += event.amount

    top_user = max(user_totals, key=user_totals.get)

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(set(event.user for event in events)),
        "revenue": revenue,
        "top_user": top_user,
    }
