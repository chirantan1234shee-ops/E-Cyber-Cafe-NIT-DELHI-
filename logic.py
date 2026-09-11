# logic.py
from sqlalchemy.orm import Session
from database import Scheme
from vector_search import semantic_scheme_match

def evaluate_eligibility(scheme: Scheme, user_profile: dict) -> dict:
    rules = scheme.rules or {}
    disqualifications = []

    age = user_profile.get("age", 0)
    income = user_profile.get("annual_income", 0.0)
    state = user_profile.get("state", "")
    category = user_profile.get("category", "")

    if "min_age" in rules and age < rules["min_age"]:
        disqualifications.append(f"Age {age} is below minimum required age of {rules['min_age']}.")
    if "max_age" in rules and age > rules["max_age"]:
        disqualifications.append(f"Age {age} exceeds maximum allowed age of {rules['max_age']}.")
    if "max_income" in rules and income > rules["max_income"]:
        disqualifications.append(f"Annual income ₹{income} exceeds upper limit of ₹{rules['max_income']}.")

    allowed_states = rules.get("allowed_states", ["All"])
    if "All" not in allowed_states and state not in allowed_states:
        disqualifications.append(f"State domicile '{state}' is not covered under this scheme.")

    eligible_cats = rules.get("eligible_categories", ["All"])
    if "All" not in eligible_cats and category not in eligible_cats:
        disqualifications.append(f"Category '{category}' does not match eligible groups.")

    is_eligible = len(disqualifications) == 0
    return {
        "scheme_id": scheme.id,
        "scheme_name": scheme.name,
        "category": scheme.category,
        "is_eligible": is_eligible,
        "disqualification_reasons": disqualifications
    }

def match_all_schemes(db: Session, user_profile: dict) -> list[dict]:
    schemes = db.query(Scheme).filter(Scheme.is_active == True).all()
    return [evaluate_eligibility(scheme, user_profile) for scheme in schemes]

def hybrid_rag_scheme_search(db: Session, user_query: str, user_profile: dict, top_k=3) -> list[dict]:
    """
    Performs a hybrid search: filters schemes by deterministic rule eligibility first,
    then ranks the eligible ones using semantic vector similarity.
    """
    schemes = db.query(Scheme).filter(Scheme.is_active == True).all()
    
    # Step 1: Evaluate strict rule constraints
    evaluated = [evaluate_eligibility(s, user_profile) for s in schemes]
    eligible_scheme_ids = {res["scheme_id"] for res in evaluated if res["is_eligible"]}
    
    eligible_schemes = [s for s in schemes if s.id in eligible_scheme_ids]
    
    if not eligible_schemes:
        return []
        
    # Step 2: Apply semantic vector search across the filtered eligible pool
    semantic_results = semantic_scheme_match(user_query, eligible_schemes, top_k=top_k)
    return semantic_results