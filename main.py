# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from logic import hybrid_rag_scheme_search, match_all_schemes
from pydantic import BaseModel

app = FastAPI(title="YojnaMitra API Gateway", version="1.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SearchRequest(BaseModel):
    user_query: str
    age: int
    annual_income: float
    state: str
    category: str

@app.post("/api/hybrid-search")
def api_hybrid_search(payload: SearchRequest, db: Session = Depends(get_db)):
    user_profile = {
        "age": payload.age,
        "annual_income": payload.annual_income,
        "state": payload.state,
        "category": payload.category
    }
    
    try:
        results = hybrid_rag_scheme_search(db, payload.user_query, user_profile, top_k=3)
        return {
            "query": payload.user_query,
            "matched_schemes": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))