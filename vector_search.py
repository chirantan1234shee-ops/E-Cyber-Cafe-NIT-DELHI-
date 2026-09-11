# vector_search.py
import torch
from sentence_transformers import SentenceTransformer, util

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def semantic_scheme_match(user_query: str, eligible_schemes: list, top_k=3) -> list[dict]:
    if not eligible_schemes:
        return []
        
    model = get_embedding_model()
    descriptions = [f"{s.name}: {s.description}" for s in eligible_schemes]
    
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    scheme_embeddings = model.encode(descriptions, convert_to_tensor=True)
    
    cos_scores = util.cos_sim(query_embedding, scheme_embeddings)[0]
    top_results = torch.topk(cos_scores, k=min(top_k, len(eligible_schemes)))
    
    results = []
    for score, idx in zip(top_results.values, top_results.indices):
        scheme = eligible_schemes[idx]
        results.append({
            "scheme_id": scheme.id,
            "scheme_name": scheme.name,
            "category": scheme.category,
            "description": scheme.description,
            "relevance_score": round(float(score) * 100, 1)
        })
        
    return results