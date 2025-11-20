import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import create_document, get_documents, db
from schemas import User, Listing, Order, Submission, Activity

app = FastAPI(title="Intel Replica API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Intel Replica Backend Running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# --- Helper models for pagination/filtering ---
class PaginationParams(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    limit: int = 24


# --- Listings Endpoints ---
@app.get("/api/listings")
def list_listings(q: Optional[str] = None, category: Optional[str] = None, limit: int = 24):
    """Fetch marketplace listings with optional search and category filter"""
    filt = {}
    if category:
        filt["category"] = category
    if q:
        # simple regex search on title or tags
        filt["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
        ]
    docs = get_documents("listing", filt, limit)
    # Convert ObjectIds to strings
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return {"items": docs}


@app.post("/api/listings", status_code=201)
def create_listing(payload: Listing):
    new_id = create_document("listing", payload)
    return {"id": new_id}


# --- Submissions Endpoints ---
@app.get("/api/submissions")
def get_submissions(limit: int = 50):
    docs = get_documents("submission", {}, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return {"items": docs}


@app.post("/api/submissions", status_code=201)
def create_submission(payload: Submission):
    new_id = create_document("submission", payload)
    # also log activity
    try:
        create_document("activity", Activity(actor_email=payload.submitter_email, action="submission_created", target=new_id))
    except Exception:
        pass
    return {"id": new_id}


# --- Users (lightweight) ---
@app.post("/api/users", status_code=201)
def create_user(user: User):
    new_id = create_document("user", user)
    return {"id": new_id}


# --- Activity feed ---
@app.get("/api/activity")
def get_activity(limit: int = 20):
    docs = get_documents("activity", {}, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return {"items": docs}


# --- Schema Introspection (optional helper) ---
@app.get("/schema")
def get_schema_definitions():
    # Provide minimal schema info for viewers/tools
    return {
        "collections": [
            {"name": "user", "fields": list(User.model_fields.keys())},
            {"name": "listing", "fields": list(Listing.model_fields.keys())},
            {"name": "order", "fields": list(Order.model_fields.keys())},
            {"name": "submission", "fields": list(Submission.model_fields.keys())},
            {"name": "activity", "fields": list(Activity.model_fields.keys())},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
