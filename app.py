# app.py
import streamlit as st
import asyncio
import requests
import os
import base64
from dotenv import load_dotenv
from database import SessionLocal, User, Application
from logic import match_all_schemes
from services.auth import DIGILOCKER_CLIENT_ID, verify_digilocker_callback

load_dotenv()

st.set_page_config(page_title="YojnaMitra CyberCafe Portal", page_icon="🇮🇳", layout="wide")

st.markdown("## 🏛️ YojnaMitra Autonomous CyberCafe Portal")
st.markdown("---")

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

def get_db():
    return SessionLocal()

# Sidebar Authentication Gateway
st.sidebar.markdown("### 🔐 CyberCafe Operator & Citizen Portal")
auth_mode = st.sidebar.radio("Select Mode", ["Login", "Register"])

db = get_db()
if auth_mode == "Register":
    st.sidebar.subheader("New User Registration")
    reg_user = st.sidebar.text_input("Username")
    reg_pass = st.sidebar.text_input("Password", type="password")
    reg_name = st.sidebar.text_input("Full Name")
    reg_age = st.sidebar.number_input("Age", 1, 120, 25)
    reg_income = st.sidebar.number_input("Annual Income (₹)", 0.0, step=10000.0, value=150000.0)
    reg_state = st.sidebar.selectbox("State", ["Uttar Pradesh", "Delhi", "Bihar", "Maharashtra", "All"])
    reg_cat = st.sidebar.selectbox("Category", ["Farmer", "Student", "Female", "Mother", "General", "OBC", "SC", "ST", "All"])
    
    if st.sidebar.button("Register Account"):
        existing = db.query(User).filter(User.username == reg_user).first()
        if existing:
            st.sidebar.error("Username already exists.")
        else:
            u = User(username=reg_user, password_hash=reg_pass, name=reg_name, age=reg_age, annual_income=reg_income, state=reg_state, category=reg_cat)
            db.add(u)
            db.commit()
            st.sidebar.success("Account created! Please switch to Login.")
else:
    st.sidebar.subheader("Portal Login")
    login_user = st.sidebar.text_input("Username")
    login_pass = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        u = db.query(User).filter(User.username == login_user, User.password_hash == login_pass).first()
        if u:
            st.session_state.logged_in_user = {"id": u.id, "name": u.name, "state": u.state, "age": u.age, "income": u.annual_income, "category": u.category}
            st.sidebar.success(f"Welcome back, {u.name}!")
        else:
            st.sidebar.error("Invalid credentials.")

db.close()

if st.session_state.logged_in_user:
    user = st.session_state.logged_in_user
    st.success(f"Active Session: **{user['name']}** (Domicile: {user['state']})")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Dynamic Eligibility Audit",
        "2. Multilingual AI Assistant",
        "3. Agentic Form Gateway",
        "4. Beneficiary Dashboard",
        "5. DigiLocker e-KYC Vault"
    ])

    with tab1:
        st.subheader("Automated Scheme Policy Matcher")
        with st.form("audit_form"):
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age", value=user["age"])
                income = st.number_input("Annual Income (₹)", value=user["income"])
            with c2:
                state = st.selectbox("State", ["Uttar Pradesh", "Delhi", "Bihar", "Maharashtra", "All"], index=0 if user["state"]=="Uttar Pradesh" else 1)
                category = st.selectbox("Category", ["Farmer", "Student", "Female", "Mother", "General", "OBC", "SC", "ST", "All"])
            submitted = st.form_submit_button("Run Rule Engine Audit")

        if submitted:
            db_session = get_db()
            results = match_all_schemes(db_session, {"age": age, "annual_income": income, "state": state, "category": category})
            db_session.close()
            
            for res in results:
                status = "✅ [ELIGIBLE]" if res["is_eligible"] else "❌ [INELIGIBLE]"
                with st.expander(f"{status} {res['scheme_name']}"):
                    if res["is_eligible"]:
                        st.success("Citizen qualifies for this scheme.")
                    else:
                        for reason in res["disqualification_reasons"]:
                            st.markdown(f"- {reason}")

        st.markdown("---")
        st.subheader("🤖 Hybrid RAG Semantic Query")
        natural_query = st.text_input("Describe your situation in plain text (e.g., 'I am a low-income farmer needing financial assistance for my crops'):")
        
        if st.button("Run Hybrid RAG Search"):
            if not natural_query:
                st.warning("Please enter a description.")
            else:
                payload = {
                    "user_query": natural_query,
                    "age": user["age"],
                    "annual_income": user["income"],
                    "state": user["state"],
                    "category": user["category"]
                }
                try:
                    res = requests.post("http://localhost:8000/api/hybrid-search", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        matched = data.get("matched_schemes", [])
                        if matched:
                            st.success(f"Found {len(matched)} semantically relevant schemes matching your profile:")
                            for item in matched:
                                with st.container():
                                    st.markdown(f"**{item['scheme_name']}** (Relevance Score: `{item['relevance_score']}%`)")
                                    st.caption(item['description'])
                                    st.markdown("---")
                        else:
                            st.info("No eligible schemes found matching that specific semantic query under your profile constraints.")
                    else:
                        st.error(f"Backend API Error: {res.text}")
                except Exception as e:
                    st.error(f"Failed to connect to FastAPI backend at port 8000: {e}")

    with tab2:
        st.subheader("Multilingual AI Kiosk Assistant (Powered by Sarvam AI)")
        
        input_mode = st.radio("Select Input Mode", ["Text Prompt", "Voice Audio (Sarvam STT)"], horizontal=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_query = ""
        if input_mode == "Text Prompt":
            user_query = st.chat_input("Ask about government schemes in Hindi, English, or regional languages...")
        else:
            st.markdown("### Upload Audio or Use Voice Interface")
            audio_file = st.file_uploader("Upload audio file (.wav / .mp3) for Sarvam Saaras STT translation", type=["wav", "mp3", "m4a"])
            if audio_file and st.button("Transcribe & Process Audio"):
                files = {"file": (audio_file.name, audio_file.getvalue(), audio_file.type)}
                data = {"model": "saaras:v1", "language_code": "hi-IN"}
                
                with st.spinner("Translating via Sarvam AI Saaras..."):
                    try:
                        response = requests.post("https://api.sarvam.ai/speech-to-text", headers={"api-subscription-key": str(os.getenv("SARVAM_API_KEY", ""))}, files=files, data=data)
                        if response.status_code == 200:
                            user_query = response.json().get("transcript", "")
                            st.success(f"Transcribed Text: {user_query}")
                        else:
                            st.error(f"Sarvam API Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection error to Sarvam AI: {e}")

        if user_query:
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)
            
            try:
                payload = {
                    "user_query": user_query,
                    "age": user["age"],
                    "annual_income": user["income"],
                    "state": user["state"],
                    "category": user["category"]
                }
                res = requests.post("http://localhost:8000/api/hybrid-search", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    matched = data.get("matched_schemes", [])
                    if matched:
                        top_scheme = matched[0]
                        reply = f"YojnaMitra AI Kiosk: Based on your query and profile in {user['state']}, the best match is **{top_scheme['scheme_name']}** (Relevance: {top_scheme['relevance_score']}%). {top_scheme['description']}"
                    else:
                        reply = f"YojnaMitra AI Kiosk: No matching schemes found for your specific query under your profile constraints in {user['state']}."
                else:
                    reply = "YojnaMitra AI Kiosk: Error connecting to the RAG backend search engine."
            except Exception as e:
                reply = f"YojnaMitra AI Kiosk: System offline or unable to reach FastAPI server: {e}"
            
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
                
                if st.button("🔊 Play Audio Response (Sarvam Bulbul TTS)", key=f"tts_{len(st.session_state.messages)}"):
                    sarvam_key = os.getenv("SARVAM_API_KEY") or ""
                    tts_headers = {"api-subscription-key": sarvam_key, "Content-Type": "application/json"}
                    tts_payload = {
                        "inputs": [reply[:450]],
                        "target_language_code": "hi-IN",
                        "speaker": "anant",
                        "model": "bulbul:v1"
                    }
                    try:
                        tts_res = requests.post("https://api.sarvam.ai/text-to-speech", headers=tts_headers, json=tts_payload)
                        if tts_res.status_code == 200:
                            audios = tts_res.json().get("audios", [])
                            if audios:
                                audio_bytes = base64.b64decode(audios[0])
                                st.audio(audio_bytes, format="audio/wav")
                        else:
                            st.error(f"TTS Error: {tts_res.text}")
                    except Exception as e:
                        st.error(f"Failed to generate speech stream: {e}")

    with tab3:
        st.subheader("Direct Form Filing Gateway")
        with st.form("filing"):
            s_name = st.text_input("Applicant Name", value=user["name"])
            target = st.selectbox("Target Scheme", ["PM Kisan Samman Nidhi", "Uttar Pradesh Matritva Sahyog Yojana"])
            if st.form_submit_button("Submit Application"):
                db_session = get_db()
                app_record = Application(user_id=user["id"], scheme_id=1, status="Submitted", payload_snapshot={"name": s_name, "scheme": target})
                db_session.add(app_record)
                db_session.commit()
                db_session.close()
                st.success("Application successfully filed and logged in database.")

    with tab4:
        st.subheader("Application Logs")
        db_session = get_db()
        apps = db_session.query(Application).filter(Application.user_id == user["id"]).all()
        db_session.close()
        if apps:
            st.dataframe([{"ID": a.id, "Status": a.status, "Time": str(a.created_at)} for a in apps])
        else:
            st.info("No applications filed yet.")

    with tab5:
        st.subheader("DigiLocker Integration Vault")
        st.markdown("Authenticate via DigiLocker to auto-populate and verify your demographic data securely.")
        
        redirect_uri = "http://localhost:8501"
        digilocker_auth_url = f"https://dg-sandbox.setu.co/api/oauth/authorize?response_type=code&client_id={DIGILOCKER_CLIENT_ID}&redirect_uri={redirect_uri}"

        query_params = st.query_params
        if "code" in query_params:
            auth_code = query_params["code"]
            st.success("Authorization code captured from DigiLocker gateway!")
            
            if st.button("Complete e-KYC Token Exchange"):
                try:
                    kyc_data = asyncio.run(verify_digilocker_callback(auth_code, redirect_uri))
                    st.session_state.digilocker_verified = True
                    st.session_state.kyc_payload = kyc_data
                    st.json(kyc_data)
                    st.success("e-KYC identity validation passed successfully via real API route.")
                except Exception as e:
                    st.error(f"Failed to exchange token with DigiLocker sandbox: {e}")
        else:
            st.markdown(f"[Click here to Authenticate with DigiLocker]({digilocker_auth_url})")
            st.info("You will be redirected to the DigiLocker gateway to authorize demographic sharing.")
else:
    st.info("Please log in or register an account using the sidebar to access the CyberCafe portal features.")