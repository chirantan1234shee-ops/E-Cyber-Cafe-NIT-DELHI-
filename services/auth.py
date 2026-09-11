# services/auth.py
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

DIGILOCKER_CLIENT_ID = os.getenv("DIGILOCKER_CLIENT_ID", "")
DIGILOCKER_CLIENT_SECRET = os.getenv("DIGILOCKER_CLIENT_SECRET", "")

async def verify_digilocker_callback(auth_code: str, redirect_uri: str) -> dict:
    """
    Exchanges the DigiLocker auth code for access tokens and fetches user KYC details.
    """
    token_url = "https://dg-sandbox.setu.co/api/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": DIGILOCKER_CLIENT_ID,
        "client_secret": DIGILOCKER_CLIENT_SECRET,
        "redirect_uri": redirect_uri
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, json=payload)
        if response.status_code != 200:
            raise Exception(f"DigiLocker Token Exchange Failed: {response.text}")
        
        token_data = response.json()
        return {
            "verified": True,
            "kyc_data": token_data
        }