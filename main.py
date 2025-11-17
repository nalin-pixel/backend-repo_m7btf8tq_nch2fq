import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from database import create_document, get_documents
from schemas import ContactMessage, CaseStudy

app = FastAPI(title="Teratherm Energy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Teratherm Energy API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Connected"
            response["collections"] = db.list_collection_names()
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Contact form endpoint
@app.post("/api/contact")
async def submit_contact(message: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", message)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Case studies listing (seeded static response + DB if available)
@app.get("/api/case-studies")
async def list_case_studies(category: str | None = None) -> List[CaseStudy]:
    filter_dict = {}
    if category:
        filter_dict["category"] = category
    try:
        docs = get_documents("casestudy", filter_dict)
        # Convert ObjectId to string and return
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception:
        # Fallback demo data if DB unconfigured
        demo = [
            {"title": "Cannes Villa", "category": "domestic", "summary": "Heating, cooling, pool, DHW.", "image_url": "/images/cannes.jpg"},
            {"title": "UK Helipad Estate", "category": "mixed", "summary": "Helipad, hangar, pool, spa.", "image_url": "/images/helipad.jpg"},
            {"title": "Stadium Project", "category": "commercial", "summary": "Large-scale commercial.", "image_url": "/images/stadium.jpg"},
            {"title": "Rawmarsh Sandhill Academy", "category": "education", "summary": "ROI-led project.", "image_url": "/images/rawmarsh.jpg"}
        ]
        return demo

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
