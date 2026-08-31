import os
from openai import OpenAI

# 🔑 Paste your OpenRouter API Key here
OPENROUTER_API_KEY = "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"

def get_real_ai_response(user_query: str, scheme: dict, profile: dict, ready_docs: list, missing_docs: list, language: str) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY") or OPENROUTER_API_KEY
    )
    
    lang_instruction = {
        "English": "Respond strictly in professional English.",
        "Hindi": "कृपया उत्तर पूरी तरह से हिंदी भाषा में दें।",
        "Hinglish": "Respond in casual Hinglish mix of Hindi and English like a helpful local advisor."
    }.get(language, "Respond in English.")

    system_prompt = f"""
You are 'YojnaMitra' (योजना मित्र), an expert Agentic AI Assistant specialized in Indian Government Schemes.
Language Preference: {lang_instruction}

YOUR AGENTIC RULES:
1. Evaluate user eligibility based on profile income (₹{profile.get('income')}) versus scheme ceiling (₹{scheme.get('max_income')}).
2. Address missing documents or DigiLocker status.
3. Be clear, structured, and helpful.

CONTEXT:
- Scheme: {scheme.get('title')} ({scheme.get('ministry')})
- Benefits: {scheme.get('summary')}
- Applicant Name: {profile.get('full_name')}
- Occupation: {profile.get('occupation')}
- State: {profile.get('state')}
- DigiLocker Verified: {'Yes' if profile.get('digilocker_verified') else 'No'}
- Ready Documents: {ready_docs}
- Missing Documents: {missing_docs}
"""

    candidate_models = [
        "meta-llama/llama-3.3-70b-instruct",
        "deepseek/deepseek-r1:free",
        "openrouter/auto"
    ]

    last_error = ""
    for model_id in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3
            )
            return completion.choices[0].message.content
        except Exception as e:
            last_error = str(e)
            continue

    return f"⚠️ **OpenRouter AI Error:** {last_error}"