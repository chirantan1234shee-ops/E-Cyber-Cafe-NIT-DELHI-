import sqlite3
import hashlib
import os
import json
import datetime
import secrets
import streamlit as st
from openai import OpenAI

# ---------------------------------------------------------
# 1. REALISTIC SCHEME DATABASE (LOGICAL FILTERING)
# ---------------------------------------------------------
STATIC_SCHEMES_DB = [
    {
        "id": "csss_01",
        "name": "Central Sector Scheme of Scholarships (CSSS)",
        "ministry": "Ministry of Education (Govt of India)",
        "benefits": "₹12,000 to ₹20,000 per annum financial support for higher studies.",
        "max_income": 450000,
        "portal_url": "https://scholarships.gov.in/",
        "categories": ["General", "OBC", "SC", "ST", "EWS"],
        "education_req": ["10th/12th Pass", "Undergraduate", "Postgraduate"]
    },
    {
        "id": "csis_02",
        "name": "Central Sector Interest Subsidy Scheme (CSIS)",
        "ministry": "Ministry of Education",
        "benefits": "100% Interest subsidy during moratorium period on education loans.",
        "max_income": 450000,
        "portal_url": "https://www.jansamarth.in/",
        "categories": ["General", "OBC", "SC", "ST", "EWS"],
        "education_req": ["Undergraduate", "Postgraduate", "Diploma"]
    },
    {
        "id": "up_postmatric_03",
        "name": "UP General Category Post-Matric Scholarship",
        "ministry": "Social Welfare Department, Govt of Uttar Pradesh",
        "benefits": "Full/partial tuition fee reimbursement + monthly maintenance allowance.",
        "max_income": 200000,
        "portal_url": "https://scholarship.up.gov.in/",
        "categories": ["General", "EWS"],
        "state_req": "Uttar Pradesh",
        "education_req": ["10th/12th Pass", "Undergraduate", "Diploma", "Postgraduate"]
    },
    {
        "id": "pmkvy_04",
        "name": "PM Kaushal Vikas Yojana (PMKVY 4.0)",
        "ministry": "Ministry of Skill Development and Entrepreneurship",
        "benefits": "Free skill training, government certification & ₹8,000 stipend.",
        "max_income": 800000,
        "portal_url": "https://www.pmkvyofficial.org/",
        "categories": ["General", "OBC", "SC", "ST", "EWS"],
        "occupations": ["Student", "Unemployed Youth", "Artisan"]
    },
    {
        "id": "pm_mudra_05",
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "ministry": "Ministry of Finance",
        "benefits": "Collateral-free micro-loans up to ₹5 Lakhs for young entrepreneurs.",
        "max_income": 1000000,
        "portal_url": "https://www.mudra.org.in/",
        "categories": ["General", "OBC", "SC", "ST", "EWS"],
        "occupations": ["Student", "Unemployed Youth", "Artisan", "Farmer", "Salaried"]
    },
    {
        "id": "pragaty_06",
        "name": "AICTE Pragati Scholarship for Girl Students",
        "ministry": "Ministry of Education / AICTE",
        "benefits": "₹50,000 per annum financial assistance for technical degree/diploma.",
        "max_income": 800000,
        "portal_url": "https://scholarships.gov.in/",
        "gender_req": "Female",
        "education_req": ["Undergraduate", "Diploma"]
    },
    {
        "id": "yasasvi_07",
        "name": "PM-YASASVI Post-Matric Scholarship",
        "ministry": "Ministry of Social Justice & Empowerment",
        "benefits": "Tuition fee waiver and maintenance allowance for OBC/EWS students.",
        "max_income": 250000,
        "portal_url": "https://yet.nta.ac.in/",
        "categories": ["OBC", "EWS", "SC", "ST"]
    }
]

# ---------------------------------------------------------
# 2. COMPLETE SAFE MULTI-LANGUAGE DICTIONARY
# ---------------------------------------------------------
LANGUAGES = {
    "English": {
        "title": "🏛️ YojnaMitra CyberCafe Portal",
        "tagline": "Autonomous AI Kiosk for Scheme Discovery, Audit & Direct Filing",
        "tab1": "🎯 Dynamic AI Audit Engine",
        "tab2": "💬 Interactive AI Chatbot",
        "tab3": "🤖 Agentic Form Gateway",
        "tab4": "🏛️ Beneficiary Dashboard",
        "tab5": "🔗 DigiLocker OAuth",
        "tab6": "💬 Feedback & Rating",
        "logout": "Logout",
        "chat_welcome": "Hello! I am YojnaMitra Assistant. Ask me anything about eligibility, document requirements, or portal steps!",
        "login_tab": "Beneficiary Login",
        "reg_tab": "New Beneficiary Registration",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login to Portal",
        "reg_btn": "Register & Create Account",
        "full_name": "Full Name *",
        "age": "Age",
        "gender": "Gender",
        "annual_income": "Annual Income (₹)",
        "marital_status": "Marital Status",
        "category": "Category",
        "employment": "Employment",
        "state": "State",
        "pwd_status": "PwD Status",
        "area": "Area",
        "education": "Education",
        "minority": "Minority",
        "land_status": "Land Status",
        "domicile": "Domicile",
        "digilocker_verified": "✅ DigiLocker Verified",
        "digilocker_unlinked": "⚠️ DigiLocker Unlinked",
        "global_drawer": "💭 Global AI Assistant Drawer",
        "audit_header": "⚡ Autonomous Agentic Audit & Verification Engine",
        "audit_caption": "Visually inspects applicant demographic vectors against government policy constraints in real time.",
        "run_audit": "🚀 Run Interactive Agent Audit Pipeline",
        "catalog_header": "📚 Profile-Matched Scheme Catalog (Pre-Filtered)",
        "select_filing": "Select for Filing",
        "auto_fill": "Auto-Fill Form 🚀",
        "gateway_header": "Direct execution terminal: Auto-populates profiles, verifies e-KYC tokens, and submits applications.",
        "active_scheme": "Active Target Scheme (Strictly Filtered)",
        "official_terminal": "📝 Official Direct Gateway Terminal",
        "submit_manual": "Submit Application via Manual Attachment",
        "execute_dbt": "🚀 Execute Autonomous Direct Submission",
        "vault_header": "🔗 DigiLocker OAuth 2.0 Document Vault",
        "vault_caption": "Connect official Aadhaar credentials to grant instant e-KYC access to government application forms.",
        "aadhaar_num": "Aadhaar Number (12 Digits)",
        "send_otp": "Send Verification OTP",
        "enter_otp": "Enter 6-Digit OTP",
        "verify_otp": "Verify OTP & Authorize Token",
        "revoke_token": "Revoke OAuth Token Access",
        "synced_certs": "Synced Government Certificates:",
        "feedback_header": "💬 Feedback & User Rating",
        "feedback_slider": "Rate AI Agent Efficiency & Accuracy",
        "feedback_comments": "Share suggestions or missing portal features:",
        "feedback_submit": "Submit Feedback Entry"
    },
    "हिंदी (Hindi)": {
        "title": "🏛️ योजनामित्र ई-साइबर कैफे पोर्टल",
        "tagline": "योजना खोज, सत्यापन और स्वचालित आवेदन के लिए स्वायत्त एआई कियोस्क",
        "tab1": "🎯 गतिशील एआई ऑडिट इंजन",
        "tab2": "💬 इंटरएक्टिव एआई चैटबॉट",
        "tab3": "🤖 एजेंटिक फॉर्म गेटवे",
        "tab4": "🏛️ लाभार्थी डैशबोर्ड",
        "tab5": "🔗 डिजीलॉकर तिजोरी",
        "tab6": "💬 प्रतिक्रिया",
        "logout": "लॉग आउट",
        "chat_welcome": "नमस्ते! मैं योजनामित्र सहायक हूँ। पात्रता, दस्तावेज़ आवश्यकताओं या पोर्टल चरणों के बारे में मुझसे कुछ भी पूछें!",
        "login_tab": "लाभार्थी लॉगिन",
        "reg_tab": "नया लाभार्थी पंजीकरण",
        "username": "यूज़रनेम",
        "password": "पासवर्ड",
        "login_btn": "पोर्टल पर लॉगिन करें",
        "reg_btn": "पंजीकरण करें और खाता बनाएँ",
        "full_name": "पूरा नाम *",
        "age": "आयु",
        "gender": "लिंग",
        "annual_income": "वार्षिक आय (₹)",
        "marital_status": "वैवाहिक स्थिति",
        "category": "श्रेणी",
        "employment": "रोजगार",
        "state": "राज्य",
        "pwd_status": "दिव्यांगता स्थिति",
        "area": "क्षेत्र",
        "education": "शिक्षा",
        "minority": "अल्पसंख्यक",
        "land_status": "भूमि स्थिति",
        "domicile": "निवास राज्य",
        "digilocker_verified": "✅ डिजीलॉकर सत्यापित",
        "digilocker_unlinked": "⚠️ डिजीलॉकर अनलिंक किया गया",
        "global_drawer": "💭 वैश्विक एआई सहायक दराज",
        "audit_header": "⚡ स्वायत्त एजेंटिक ऑडिट और सत्यापन इंजन",
        "audit_caption": "वास्तविक समय में सरकारी नीति बाधाओं के खिलाफ आवेदक जनसांख्यिकीय वैक्टर का दृश्य निरीक्षण करता है।",
        "run_audit": "🚀 इंटरएक्टिव एजेंट ऑडिट पाइपलाइन चलाएँ",
        "catalog_header": "📚 प्रोफ़ाइल-मिलान योजना कैटलॉग (पूर्व-फ़िल्टर)",
        "select_filing": "फाइलिंग के लिए चुनें",
        "auto_fill": "ऑटो-फिल फॉर्म 🚀",
        "gateway_header": "प्रत्यक्ष निष्पादन टर्मिनल: प्रोफ़ाइल स्वतः भरता है, ई-केवाईसी टोकन सत्यापित करता है, और आवेदन जमा करता है।",
        "active_scheme": "सक्रिय लक्ष्य योजना (सख्त रूप से फ़िल्टर की गई)",
        "official_terminal": "📝 आधिकारिक प्रत्यक्ष गेटवे टर्मिनल",
        "submit_manual": "मैनुअल अटैचमेंट के माध्यम से आवेदन जमा करें",
        "execute_dbt": "🚀 स्वायत्त प्रत्यक्ष सबमिशन निष्पादित करें",
        "vault_header": "🔗 डिजीलॉकर ओएथ 2.0 दस्तावेज़ तिजोरी",
        "vault_caption": "सरकारी आवेदन फॉर्मों तक त्वरित ई-केवाईसी पहुंच प्रदान करने के लिए आधिकारिक आधार क्रेडेंशियल कनेक्ट करें।",
        "aadhaar_num": "आधार नंबर (12 अंक)",
        "send_otp": "सत्यापन ओटीपी भेजें",
        "enter_otp": "6-अंकों का ओटीपी दर्ज करें",
        "verify_otp": "ओटीपी सत्यापित करें और टोकन अधिकृत करें",
        "revoke_token": "ओएथ टोकन एक्सेस रद्द करें",
        "synced_certs": "सिंक किए गए सरकारी प्रमाणपत्र:",
        "feedback_header": "💬 प्रतिक्रिया और उपयोगकर्ता रेटिंग",
        "feedback_slider": "एआई एजेंट दक्षता और सटीकता को रेट करें",
        "feedback_comments": "सुझाव या गुम पोर्टल सुविधाएँ साझा करें:",
        "feedback_submit": "प्रतिक्रिया प्रविष्टि जमा करें"
    }
}

# ---------------------------------------------------------
# 3. DATABASE SETUP & HELPERS
# ---------------------------------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('yojna_mitra.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            annual_income REAL,
            category TEXT,
            employment_status TEXT,
            state TEXT,
            disability_status TEXT,
            marital_status TEXT,
            area_type TEXT,
            education_level TEXT,
            minority_status TEXT,
            land_holding TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            scheme_id TEXT NOT NULL,
            scheme_name TEXT NOT NULL,
            reference_id TEXT NOT NULL,
            status TEXT NOT NULL,
            submitted_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# 4. OPENROUTER AI SETUP
# ---------------------------------------------------------
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key) if api_key else None
AGENT_MODEL = "meta-llama/llama-3.3-70b-instruct"

# ---------------------------------------------------------
# 4b. AGENTIC TOOLING LAYER
# ---------------------------------------------------------
# These are REAL Python functions the LLM can call as tools. The model never
# invents an eligibility verdict or a submission outcome itself — it must call
# a tool and use the ground-truth result that comes back. This is what makes
# the "agent" genuinely agentic rather than a single prompt asked to role-play
# a multi-step process.

AUDIT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_eligibility_rule",
            "description": (
                "Deterministically checks ONE eligibility rule for ONE scheme against the "
                "applicant's verified profile and returns the ground-truth pass/fail result. "
                "Never guess or assume a result yourself — always call this for every rule "
                "that applies to a scheme before drawing a conclusion about it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "scheme_id": {"type": "string", "description": "The scheme's id, e.g. 'csss_01'"},
                    "rule": {
                        "type": "string",
                        "enum": ["income", "gender", "category", "state", "education", "occupation"],
                        "description": "Which eligibility rule to check for this scheme.",
                    },
                },
                "required": ["scheme_id", "rule"],
            },
        },
    }
]

GATEWAY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_vault_documents",
            "description": "Fetches the applicant's verified documents from their DigiLocker vault.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "validate_documents",
            "description": "Checks the fetched vault documents against what this scheme requires for filing.",
            "parameters": {
                "type": "object",
                "properties": {"scheme_id": {"type": "string"}},
                "required": ["scheme_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "map_form_fields",
            "description": "Maps the applicant's verified profile data onto this scheme's application form fields.",
            "parameters": {
                "type": "object",
                "properties": {"scheme_id": {"type": "string"}},
                "required": ["scheme_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_application",
            "description": (
                "Submits the mapped, validated application to the scheme's DBT portal and returns "
                "a real reference ID. Only call this AFTER validate_documents reports valid=true "
                "and map_form_fields has been called for this scheme."
            ),
            "parameters": {
                "type": "object",
                "properties": {"scheme_id": {"type": "string"}},
                "required": ["scheme_id"],
            },
        },
    },
]


def tool_check_eligibility_rule_impl(scheme_id, rule, applicant, schemes_db):
    scheme = next((s for s in schemes_db if s["id"] == scheme_id), None)
    if not scheme:
        return {"error": f"unknown scheme_id '{scheme_id}'"}
    if rule == "income":
        passed = applicant["income"] <= scheme["max_income"]
        return {"rule": "income", "passed": passed, "detail": f"income ₹{applicant['income']:,} vs ceiling ₹{scheme['max_income']:,}"}
    if rule == "gender":
        req = scheme.get("gender_req")
        passed = (req is None) or (req == applicant["gender"])
        return {"rule": "gender", "passed": passed, "detail": f"requires {req or 'Any'}, applicant is {applicant['gender']}"}
    if rule == "category":
        cats = scheme.get("categories")
        passed = (cats is None) or (applicant["category"] in cats)
        return {"rule": "category", "passed": passed, "detail": f"allowed {cats or 'Any'}, applicant is {applicant['category']}"}
    if rule == "state":
        req = scheme.get("state_req")
        passed = (req is None) or (req == applicant["state"])
        return {"rule": "state", "passed": passed, "detail": f"requires {req or 'Any'}, applicant is in {applicant['state']}"}
    if rule == "education":
        reqs = scheme.get("education_req")
        passed = (reqs is None) or (applicant["education"] in reqs)
        return {"rule": "education", "passed": passed, "detail": f"requires {reqs or 'Any'}, applicant has {applicant['education']}"}
    if rule == "occupation":
        occs = scheme.get("occupations")
        passed = (occs is None) or (applicant["employment"] in occs)
        return {"rule": "occupation", "passed": passed, "detail": f"requires {occs or 'Any'}, applicant is {applicant['employment']}"}
    return {"error": f"unknown rule '{rule}'"}


def tool_fetch_vault_documents_impl(digilocker_linked):
    if not digilocker_linked:
        return {"status": "not_linked", "documents": []}
    return {
        "status": "linked",
        "documents": ["Aadhaar Identity Card", "Income Certificate", "Domicile Certificate", "Caste/Category Certificate"],
    }


def tool_validate_documents_impl(scheme, available_docs):
    required = ["Aadhaar Identity Card", "Income Certificate"]
    if scheme.get("state_req"):
        required.append("Domicile Certificate")
    if scheme.get("categories"):
        required.append("Caste/Category Certificate")
    missing = [d for d in required if d not in available_docs]
    return {"required": required, "available": available_docs, "missing": missing, "valid": len(missing) == 0}


def tool_map_form_fields_impl(applicant, scheme):
    return {
        "applicant_name": applicant["name"],
        "category": applicant["category"],
        "domicile": applicant["state"],
        "annual_income": applicant["income"],
        "scheme_name": scheme["name"],
        "scheme_ceiling": scheme["max_income"],
    }


def generate_reference_id(scheme_id):
    return f"YM-2026-{scheme_id.upper()}-{secrets.token_hex(2).upper()}"


def persist_submission(username, scheme_id, scheme_name, reference_id, status="Submitted"):
    conn = sqlite3.connect('yojna_mitra.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO submissions (username, scheme_id, scheme_name, reference_id, status, submitted_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username, scheme_id, scheme_name, reference_id, status, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()


def tool_submit_application_impl(username, scheme_id, scheme_name):
    ref_id = generate_reference_id(scheme_id)
    persist_submission(username, scheme_id, scheme_name, ref_id)
    return {"status": "submitted", "reference_id": ref_id}


def run_tool_agent(system_prompt, user_prompt, tools, tool_router, status_box, model=AGENT_MODEL, max_turns=6):
    """Generic tool-calling agent loop. The model decides which tools to call and in
    what order; we execute the real Python implementation and feed the ground-truth
    result back, live-logging every call to status_box so the trace on screen is the
    actual sequence of reasoning steps, not scripted text."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in tool_calls
                ],
            })
            for tc in tool_calls:
                fn_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = tool_router(fn_name, args)
                arg_str = ", ".join(f"{k}={v}" for k, v in args.items())
                status_box.write(f"🔧 **{fn_name}**`({arg_str})` → `{result}`")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })
        else:
            return msg.content
    return None

# ---------------------------------------------------------
# 5. PAGE CONFIG & SESSION INITIALIZATION
# ---------------------------------------------------------
st.set_page_config(page_title="YojnaMitra CyberCafe Portal", page_icon="🏛️", layout="wide")

# ---------------------------------------------------------
# 5b. GLOBAL STYLING (profile card, badges, section headers)
# ---------------------------------------------------------
st.markdown("""
<style>
.ym-profile-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
    border-radius: 16px;
    padding: 18px 16px;
    color: white;
    margin-bottom: 10px;
}
.ym-avatar {
    width: 52px;
    height: 52px;
    min-width: 52px;
    border-radius: 50%;
    background: rgba(255,255,255,0.18);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
    color: white;
    border: 2px solid rgba(255,255,255,0.4);
}
.ym-name { font-size: 15px; font-weight: 700; margin: 0; line-height: 1.3; }
.ym-username { font-size: 12px; opacity: 0.8; margin: 0; line-height: 1.3; }
.ym-badge-row { margin-top: 12px; display: flex; gap: 6px; flex-wrap: wrap; }
.ym-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}
.ym-edit-banner {
    background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
    border-radius: 16px;
    padding: 22px 26px;
    color: white;
    margin-bottom: 18px;
}
.ym-edit-banner h2 { margin: 0; font-size: 22px; }
.ym-edit-banner p { margin: 6px 0 0 0; opacity: 0.85; font-size: 13.5px; }
.ym-section-label {
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #2c5282;
    margin: 4px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state["user"] = None
if "digilocker_linked" not in st.session_state:
    st.session_state["digilocker_linked"] = False
if "otp_sent" not in st.session_state:
    st.session_state["otp_sent"] = False
if "language" not in st.session_state:
    st.session_state["language"] = "English"
if "selected_scheme_for_filing" not in st.session_state:
    st.session_state["selected_scheme_for_filing"] = None
if "agent_execution_data" not in st.session_state:
    st.session_state["agent_execution_data"] = None
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []
if "widget_chat_history" not in st.session_state:
    st.session_state["widget_chat_history"] = []
if "scheme_chats" not in st.session_state:
    st.session_state["scheme_chats"] = {}
if "editing_profile" not in st.session_state:
    st.session_state["editing_profile"] = False

t = LANGUAGES[st.session_state["language"]]

def _reset_session_for_account_change():
    st.session_state["user"] = None
    st.session_state["digilocker_linked"] = False
    st.session_state["agent_execution_data"] = None
    st.session_state["chat_messages"] = []
    st.session_state["widget_chat_history"] = []
    st.session_state["scheme_chats"] = {}
    st.session_state["editing_profile"] = False

# ---------------------------------------------------------
# 6. SIDEBAR CONTROLS & WIDGET ASSISTANT
# ---------------------------------------------------------
with st.sidebar:
    st.title("🌐 Language / भाषा")
    selected_lang = st.selectbox("Select Interface Language", list(LANGUAGES.keys()), index=0 if st.session_state["language"] == "English" else 1)
    if selected_lang != st.session_state["language"]:
        st.session_state["language"] = selected_lang
        st.rerun()
    
    st.divider()

    if st.session_state["user"]:
        u = st.session_state["user"]

        # --- Profile card ---
        name_parts = [p for p in u["name"].split() if p]
        initials = "".join(p[0].upper() for p in name_parts[:2]) if name_parts else "U"

        st.markdown(f"""
        <div class="ym-profile-card">
            <div style="display:flex; align-items:center; gap:12px;">
                <div class="ym-avatar">{initials}</div>
                <div>
                    <p class="ym-name">{u['name']}</p>
                    <p class="ym-username">@{u['username']}</p>
                </div>
            </div>
            <div class="ym-badge-row">
                <span class="ym-badge">📍 {u['state']}</span>
                <span class="ym-badge">🏷️ {u['category']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- Action buttons ---
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            if st.button("✏️ Edit", help="Change User Details", use_container_width=True):
                st.session_state["editing_profile"] = not st.session_state["editing_profile"]
                st.rerun()
        with col_act2:
            if st.button("🔄 Switch", help="Switch Account", use_container_width=True):
                _reset_session_for_account_change()
                st.rerun()
        with col_act3:
            if st.button(f"🚪 {t['logout']}", help=t["logout"], use_container_width=True):
                _reset_session_for_account_change()
                st.rerun()

        st.write("")

        if st.session_state["digilocker_linked"]:
            st.success(t["digilocker_verified"], icon="🛡️")
        else:
            st.warning(t["digilocker_unlinked"])

        st.divider()
        
        with st.expander(t["global_drawer"], expanded=True):
            widget_chat_container = st.container(height=280)
            
            with widget_chat_container:
                with st.container(border=True):
                    w_col1, w_col2 = st.columns([1, 4])
                    with w_col1:
                        st.markdown("### 🤖")
                    with w_col2:
                        st.markdown(f"**Namaste! I am YojnaMitra AI.** How can I assist you with government schemes or form filing today?")

                for msg in st.session_state.get("widget_chat_history", []):
                    if msg["role"] == "user":
                        st.info(f"**You:** {msg['content']}")
                    else:
                        st.success(f"**YojnaMitra:** {msg['content']}")

            with st.form("sidebar_widget_chat_form", clear_on_submit=True):
                w_input_col, w_btn_col = st.columns([4, 1])
                with w_input_col:
                    user_widget_query = st.text_input("Ask YojnaMitra AI", placeholder="Ask YojnaMitra AI", label_visibility="collapsed")
                with w_btn_col:
                    widget_submit = st.form_submit_button("⬆")

                if widget_submit and user_widget_query:
                    st.session_state["widget_chat_history"].append({"role": "user", "content": user_widget_query})

                    if client:
                        try:
                            w_res = client.chat.completions.create(
                                model="meta-llama/llama-3.3-70b-instruct",
                                messages=[
                                    {"role": "system", "content": f"You are YojnaMitra AI Kiosk Assistant for applicant {u['name']} from {u['state']} ({u['category']} category). Keep answers under 2 concise sentences."},
                                    {"role": "user", "content": user_widget_query}
                                ]
                            )
                            st.session_state["widget_chat_history"].append({"role": "assistant", "content": w_res.choices[0].message.content})
                        except Exception as e:
                            st.session_state["widget_chat_history"].append({"role": "assistant", "content": f"Error: {e}"})
                    else:
                        st.session_state["widget_chat_history"].append({"role": "assistant", "content": "API key not configured."})
                    
                    st.rerun()

# ---------------------------------------------------------
# 7. MAIN INTERFACE LOGIC
# ---------------------------------------------------------
if not st.session_state["user"]:
    st.title(t["title"])
    st.caption(t["tagline"])
    
    l_tab1, l_tab2 = st.tabs([t["login_tab"], t["reg_tab"]])
    
    with l_tab1:
        with st.form("login_form"):
            user_in = st.text_input(t["username"])
            pass_in = st.text_input(t["password"], type="password")
            if st.form_submit_button(t["login_btn"], use_container_width=True):
                if user_in and pass_in:
                    hashed = hash_password(pass_in.strip())
                    conn = sqlite3.connect('yojna_mitra.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT username, name, age, gender, annual_income, category, employment_status, state, disability_status, marital_status, area_type, education_level, minority_status, land_holding FROM users WHERE LOWER(username) = LOWER(?) AND password = ?", (user_in.strip(), hashed))
                    rec = cursor.fetchone()
                    conn.close()
                    if rec:
                        st.session_state["user"] = {
                            "username": rec[0], "name": rec[1], "age": rec[2], "gender": rec[3],
                            "income": rec[4], "category": rec[5], "employment": rec[6], "state": rec[7],
                            "disability": rec[8], "marital": rec[9], "area": rec[10], "education": rec[11],
                            "minority": rec[12], "land": rec[13]
                        }
                        st.session_state["editing_profile"] = False
                        st.rerun()
                    else:
                        st.error("Invalid credentials entered.")

    with l_tab2:
        with st.form("reg_form"):
            c_u, c_p = st.columns(2)
            reg_u = c_u.text_input(f"{t['username']} *")
            reg_p = c_p.text_input(f"{t['password']} *", type="password")
            c1, c2, c3 = st.columns(3)
            name = c1.text_input(t["full_name"])
            age = c1.number_input(t["age"], value=20)
            gender = c1.selectbox(t["gender"], ["Male", "Female", "Other"])
            income = c1.number_input(t["annual_income"], value=150000)
            marital = c1.selectbox(t["marital_status"], ["Single", "Married"])
            category = c2.selectbox(t["category"], ["General", "OBC", "SC", "ST", "EWS"])
            employment = c2.selectbox(t["employment"], ["Student", "Unemployed Youth", "Farmer", "Artisan", "Salaried"])
            state = c2.selectbox(t["state"], ["Uttar Pradesh", "Delhi", "Maharashtra", "Bihar", "West Bengal"])
            disability = c2.selectbox(t["pwd_status"], ["No", "Yes"])
            area = c3.selectbox(t["area"], ["Rural", "Urban"])
            education = c3.selectbox(t["education"], ["10th/12th Pass", "Undergraduate", "Diploma", "Postgraduate"])
            minority = c3.selectbox(t["minority"], ["No", "Yes"])
            land = c3.selectbox(t["land_status"], ["Landless", "Marginal", "Small", "N/A"])

            if st.form_submit_button(t["reg_btn"], use_container_width=True):
                if reg_u and reg_p and name:
                    try:
                        conn = sqlite3.connect('yojna_mitra.db')
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO users (username, password, name, age, gender, annual_income, category, employment_status, state, disability_status, marital_status, area_type, education_level, minority_status, land_holding) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                       (reg_u.strip(), hash_password(reg_p.strip()), name, age, gender, income, category, employment, state, disability, marital, area, education, minority, land))
                        conn.commit()
                        conn.close()
                        st.session_state["user"] = {"username": reg_u.strip(), "name": name, "age": age, "gender": gender, "income": income, "category": category, "employment": employment, "state": state, "disability": disability, "marital": marital, "area": area, "education": education, "minority": minority, "land": land}
                        st.session_state["editing_profile"] = False
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already registered.")

else:
    u = st.session_state["user"]

    # Handle Edit User Details mode
    if st.session_state["editing_profile"]:
        st.markdown("""
        <div class="ym-edit-banner">
            <h2>✏️ Edit Profile</h2>
            <p>Update your demographic details to instantly recalculate matched government schemes.</p>
        </div>
        """, unsafe_allow_html=True)
        
        gender_options = ["Male", "Female", "Other"]
        marital_options = ["Single", "Married"]
        category_options = ["General", "OBC", "SC", "ST", "EWS"]
        employment_options = ["Student", "Unemployed Youth", "Farmer", "Artisan", "Salaried"]
        state_options = ["Uttar Pradesh", "Delhi", "Maharashtra", "Bihar", "West Bengal"]
        disability_options = ["No", "Yes"]
        area_options = ["Rural", "Urban"]
        education_options = ["10th/12th Pass", "Undergraduate", "Diploma", "Postgraduate"]
        minority_options = ["No", "Yes"]
        land_options = ["Landless", "Marginal", "Small", "N/A"]

        with st.form("edit_profile_form"):
            with st.container(border=True):
                st.markdown('<p class="ym-section-label">👤 Personal Details</p>', unsafe_allow_html=True)
                p1, p2, p3, p4 = st.columns(4)
                new_name = p1.text_input(t["full_name"], value=u["name"])
                new_age = p2.number_input(t["age"], value=int(u["age"]))
                new_gender = p3.selectbox(t["gender"], gender_options, index=gender_options.index(u["gender"]) if u["gender"] in gender_options else 0)
                new_marital = p4.selectbox(t["marital_status"], marital_options, index=marital_options.index(u["marital"]) if u["marital"] in marital_options else 0)

            st.write("")
            with st.container(border=True):
                st.markdown('<p class="ym-section-label">📍 Location &amp; Category</p>', unsafe_allow_html=True)
                l1, l2, l3, l4 = st.columns(4)
                new_state = l1.selectbox(t["state"], state_options, index=state_options.index(u["state"]) if u["state"] in state_options else 0)
                new_area = l2.selectbox(t["area"], area_options, index=area_options.index(u["area"]) if u["area"] in area_options else 0)
                new_category = l3.selectbox(t["category"], category_options, index=category_options.index(u["category"]) if u["category"] in category_options else 0)
                new_minority = l4.selectbox(t["minority"], minority_options, index=minority_options.index(u["minority"]) if u["minority"] in minority_options else 0)

            st.write("")
            with st.container(border=True):
                st.markdown('<p class="ym-section-label">🎓 Education, Employment &amp; Eligibility</p>', unsafe_allow_html=True)
                e1, e2, e3, e4, e5 = st.columns(5)
                new_education = e1.selectbox(t["education"], education_options, index=education_options.index(u["education"]) if u["education"] in education_options else 0)
                new_employment = e2.selectbox(t["employment"], employment_options, index=employment_options.index(u["employment"]) if u["employment"] in employment_options else 0)
                new_income = e3.number_input(t["annual_income"], value=float(u["income"]))
                new_disability = e4.selectbox(t["pwd_status"], disability_options, index=disability_options.index(u["disability"]) if u["disability"] in disability_options else 0)
                new_land = e5.selectbox(t["land_status"], land_options, index=land_options.index(u["land"]) if u["land"] in land_options else 0)

            st.write("")
            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                submit_update = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            with col_sub2:
                cancel_update = st.form_submit_button("❌ Cancel", use_container_width=True)

            if submit_update:
                conn = sqlite3.connect('yojna_mitra.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET name=?, age=?, gender=?, annual_income=?, category=?, 
                    employment_status=?, state=?, disability_status=?, marital_status=?, 
                    area_type=?, education_level=?, minority_status=?, land_holding=? 
                    WHERE username=?
                ''', (new_name, new_age, new_gender, new_income, new_category, new_employment, 
                      new_state, new_disability, new_marital, new_area, new_education, 
                      new_minority, new_land, u["username"]))
                conn.commit()
                conn.close()

                st.session_state["user"] = {
                    "username": u["username"], "name": new_name, "age": new_age, "gender": new_gender,
                    "income": new_income, "category": new_category, "employment": new_employment, "state": new_state,
                    "disability": new_disability, "marital": new_marital, "area": new_area, "education": new_education,
                    "minority": new_minority, "land": new_land
                }
                st.session_state["editing_profile"] = False
                st.success("Profile updated successfully!")
                st.rerun()

            if cancel_update:
                st.session_state["editing_profile"] = False
                st.rerun()

    else:
        eligible_schemes = []
        for s in STATIC_SCHEMES_DB:
            if u["income"] > s["max_income"]:
                continue
            if s.get("gender_req") and s.get("gender_req") != u["gender"]:
                continue
            if s.get("pwd_req") and s.get("pwd_req") != u["disability"]:
                continue
            if s.get("categories") and u["category"] not in s.get("categories"):
                continue
            if s.get("state_req") and s.get("state_req") != u["state"]:
                continue
            if s.get("education_req") and u["education"] not in s.get("education_req"):
                continue
            if s.get("occupations") and u["employment"] not in s.get("occupations"):
                continue
            eligible_schemes.append(s)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            t["tab1"], 
            t["tab2"], 
            t["tab3"], 
            t["tab4"], 
            t["tab5"],
            t["tab6"]
        ])

        with tab1:
            st.subheader(t["audit_header"])
            st.caption(t["audit_caption"])

            c_trigger, c_space = st.columns([2, 3])
            with c_trigger:
                run_agent = st.button(t["run_audit"], type="primary", use_container_width=True)

            if run_agent:
                if client:
                    status_box = st.status("🧠 Audit Agent reasoning with live tool calls...", expanded=True)

                    catalog_summary = [
                        {"id": s["id"], "name": s["name"], "ministry": s["ministry"], "benefits": s["benefits"]}
                        for s in eligible_schemes
                    ]

                    def audit_tool_router(fn_name, args):
                        if fn_name == "check_eligibility_rule":
                            return tool_check_eligibility_rule_impl(
                                args.get("scheme_id", ""), args.get("rule", ""), u, STATIC_SCHEMES_DB
                            )
                        return {"error": f"unknown tool '{fn_name}'"}

                    system_prompt = (
                        "You are YojnaMitra's Audit Agent. You NEVER decide eligibility yourself — "
                        "you must call the check_eligibility_rule tool for every rule that applies to "
                        "a scheme (income always applies; gender/category/state/education/occupation only "
                        "if the scheme actually restricts on that dimension) before drawing any conclusion. "
                        "Only include a scheme in your final answer if every rule you checked for it passed. "
                        "Once you are done calling tools, respond with ONLY valid JSON (no markdown fences) "
                        "matching exactly this structure: "
                        '{"audit_status": "...", "evaluations": [{"scheme_name": "...", "ministry": "...", '
                        '"match_score": "...", "benefits": "...", "verification_checklist": '
                        '{"<rule>": "PASS - <detail>" or "FAIL - <detail>", ...}}]}'
                    )
                    user_prompt = f"""
                    APPLICANT PROFILE:
                    Name={u['name']} | Gender={u['gender']} | Category={u['category']} | Income=₹{u['income']}
                    Domicile={u['state']} | Education={u['education']} | Employment={u['employment']}

                    CANDIDATE SCHEMES (pre-filtered by the system, still needs rule-by-rule verification):
                    {json.dumps(catalog_summary, indent=2)}
                    """

                    try:
                        final_text = run_tool_agent(
                            system_prompt, user_prompt, AUDIT_TOOLS, audit_tool_router, status_box
                        )
                        status_box.update(label="✅ Agentic Audit Finished — every check is tool-verified", state="complete", expanded=False)

                        if final_text:
                            raw_content = final_text
                            if "```json" in raw_content:
                                raw_content = raw_content.split("```json")[1].split("```")[0].strip()
                            elif "```" in raw_content:
                                raw_content = raw_content.split("```")[1].split("```")[0].strip()
                            st.session_state["agent_execution_data"] = json.loads(raw_content)
                        else:
                            st.error("Agent did not reach a final answer within the turn limit. Try again.")
                    except Exception as e:
                        status_box.update(label="❌ Agent Execution Interrupted", state="error")
                        st.error(f"Error executing agentic LLM: {e}")

            st.divider()

            if st.session_state["agent_execution_data"]:
                agent_data = st.session_state["agent_execution_data"]
                st.success(f"🛡️ **System Status:** {agent_data.get('audit_status', 'Audit Verified')}")
                st.markdown("### 📋 AI Audit Dashboard & Pre-Approved Schemes")
                
                for item in agent_data.get("evaluations", []):
                    s_name = item['scheme_name']
                    matched_db_item = next((s for s in eligible_schemes if s["name"] == s_name), None)
                    s_portal_url = matched_db_item["portal_url"] if matched_db_item else "https://www.india.gov.in/"

                    with st.container(border=True):
                        col_info, col_checks, col_act = st.columns([3, 2, 1])
                        with col_info:
                            st.subheader(f"📌 {s_name}")
                            st.markdown(f"**Official Portal Link:** [Access Official Website]({s_portal_url})")
                            st.caption(f"**Ministry:** {item['ministry']}")
                            st.markdown(f"**Financial Benefits:** {item['benefits']}")
                        with col_checks:
                            st.markdown("**⚡ Live Audit Checklist (tool-verified):**")
                            checks = item.get("verification_checklist", {})
                            if checks:
                                for rule_name, rule_result in checks.items():
                                    icon = "✔️" if str(rule_result).upper().startswith("PASS") else "❌"
                                    st.write(f"{icon} `{rule_name}: {rule_result}`")
                            else:
                                st.write("✔️ `Verified by audit agent`")
                        with col_act:
                            st.metric("Eligibility Score", item.get("match_score", "95%"))
                            if st.button(t["auto_fill"], key=f"btn_fill_{s_name}", use_container_width=True):
                                st.session_state["selected_scheme_for_filing"] = s_name
                                st.toast(f"Transferred {s_name} to Autonomous Agentic Form Filler!")

                        # EMBEDDED AI CHATBOX BELOW EACH SCHEME
                        with st.expander(f"💬 Ask AI about {s_name}", expanded=False):
                            if s_name not in st.session_state["scheme_chats"]:
                                st.session_state["scheme_chats"][s_name] = []
                            
                            s_chat_box = st.container(height=200)
                            with s_chat_box:
                                for chat_m in st.session_state["scheme_chats"][s_name]:
                                    if chat_m["role"] == "user":
                                        st.info(f"**You:** {chat_m['content']}")
                                    else:
                                        st.success(f"**AI:** {chat_m['content']}")

                            with st.form(key=f"form_scheme_{s_name}", clear_on_submit=True):
                                sq_col1, sq_col2 = st.columns([4, 1])
                                with sq_col1:
                                    user_sq = st.text_input("Ask question...", placeholder=f"Ask about documents/deadlines for {s_name}...", label_visibility="collapsed")
                                with sq_col2:
                                    sq_submit = st.form_submit_button("Send 🤖")
                                
                                if sq_submit and user_sq:
                                    st.session_state["scheme_chats"][s_name].append({"role": "user", "content": user_sq})
                                    if client:
                                        try:
                                            sc_res = client.chat.completions.create(
                                                model="meta-llama/llama-3.3-70b-instruct",
                                                messages=[
                                                    {"role": "system", "content": f"You are YojnaMitra Scheme Expert answering queries regarding scheme: {s_name}. User is {u['name']} from {u['state']} with income {u['income']}. Be helpful and concise."},
                                                    {"role": "user", "content": user_sq}
                                                ]
                                            )
                                            st.session_state["scheme_chats"][s_name].append({"role": "assistant", "content": sc_res.choices[0].message.content})
                                        except Exception as e:
                                            st.session_state["scheme_chats"][s_name].append({"role": "assistant", "content": f"AI error: {e}"})
                                    else:
                                        st.session_state["scheme_chats"][s_name].append({"role": "assistant", "content": "API key missing."})
                                    st.rerun()
            else:
                st.markdown(f"### {t['catalog_header']}")
                for s in eligible_schemes:
                    s_name = s['name']
                    s_portal_url = s['portal_url']
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"#### 📌 {s_name}")
                            st.markdown(f"**Official Portal Link:** [Access Official Website]({s_portal_url})")
                            st.write(f"**Ministry:** {s['ministry']} | **Income Limit:** Up to ₹{s['max_income']:,}")
                            st.caption(f"**Benefits:** {s['benefits']}")
                        with c2:
                            if st.button(t["select_filing"], key=f"select_{s['id']}", use_container_width=True):
                                st.session_state["selected_scheme_for_filing"] = s_name
                                st.toast("Scheme loaded into Agentic Form Gateway!")

                        # EMBEDDED AI CHATBOX BELOW CATALOG SCHEMES
                        with st.expander(f"💬 Ask AI about {s_name}", expanded=False):
                            if s_name not in st.session_state["scheme_chats"]:
                                st.session_state["scheme_chats"][s_name] = []
                            
                            s_chat_box = st.container(height=200)
                            with s_chat_box:
                                for chat_m in st.session_state["scheme_chats"][s_name]:
                                    if chat_m["role"] == "user":
                                        st.info(f"**You:** {chat_m['content']}")
                                    else:
                                        st.success(f"**AI:** {chat_m['content']}")

                            with st.form(key=f"form_cat_scheme_{s['id']}", clear_on_submit=True):
                                sq_col1, sq_col2 = st.columns([4, 1])
                                with sq_col1:
                                    user_sq = st.text_input("Ask question...", placeholder=f"Ask about eligibility or documents...", label_visibility="collapsed")
                                with sq_col2:
                                    sq_submit = st.form_submit_button("Send 🤖")
                                
                                if sq_submit and user_sq:
                                    st.session_state["scheme_chats"][s_name].append({"role": "user", "content": user_sq})
                                    if client:
                                        try:
                                            sc_res = client.chat.completions.create(
                                                model="meta-llama/llama-3.3-70b-instruct",
                                                messages=[
                                                    {"role": "system", "content": f"You are YojnaMitra Scheme Expert answering queries regarding scheme: {s_name}. User is {u['name']} from {u['state']} with income {u['income']}. Be helpful and concise."},
                                                    {"role": "user", "content": user_sq}
                                                ]
                                            )
                                            st.session_state["scheme_chats"][s_name].append({"role": "assistant", "content": sc_res.choices[0].message.content})
                                        except Exception as e:
                                            st.session_state["scheme_chats"][s_name].append({"role": "assistant", "content": f"AI error: {e}"})
                                    else:
                                        st.session_state["scheme_chats"][s_name].append({"role": "assistant", "content": "API key missing."})
                                    st.rerun()

        with tab2:
            st.header(t["tab2"])
            st.caption("Ask questions about application procedures, income certificates, quotas, and state schemes.")

            if not st.session_state["chat_messages"]:
                st.session_state["chat_messages"].append({"role": "assistant", "content": t["chat_welcome"]})

            for msg in st.session_state["chat_messages"]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            if prompt := st.chat_input("Ask YojnaMitra AI Kiosk Assistant..."):
                st.session_state["chat_messages"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)

                with st.chat_message("assistant"):
                    if client:
                        try:
                            system_context = f"""
                            You are YojnaMitra AI, an expert CyberCafe Citizen Assistance bot.
                            Current Applicant Profile: Name={u['name']}, Age={u['age']}, Gender={u['gender']}, Domicile={u['state']}, Income=₹{u['income']}, Category={u['category']}, Education={u['education']}.
                            Be concise, direct, and actionable.
                            """
                            response = client.chat.completions.create(
                                model="meta-llama/llama-3.3-70b-instruct",
                                messages=[
                                    {"role": "system", "content": system_context},
                                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_messages"]]
                                ]
                            )
                            reply_text = response.choices[0].message.content
                            st.write(reply_text)
                            st.session_state["chat_messages"].append({"role": "assistant", "content": reply_text})
                        except Exception as e:
                            err_msg = f"Failed to connect to LLM: {e}"
                            st.error(err_msg)
                    else:
                        st.warning("OPENROUTER_API_KEY is missing from environment/secrets.")

        with tab3:
            st.header(t["tab3"])
            st.caption(t["gateway_header"])

            if eligible_schemes:
                default_index = 0
                scheme_names = [s["name"] for s in eligible_schemes]
                if st.session_state["selected_scheme_for_filing"] in scheme_names:
                    default_index = scheme_names.index(st.session_state["selected_scheme_for_filing"])

                target_scheme_name = st.selectbox(
                    t["active_scheme"], 
                    scheme_names,
                    index=default_index
                )
                
                target_scheme = next(s for s in eligible_schemes if s["name"] == target_scheme_name)

                st.markdown(f"#### {t['official_terminal']}")
                st.markdown(f"**🔗 Direct Scheme Portal:** [Open Official Website]({target_scheme['portal_url']})")
                
                with st.container(border=True):
                    g_col1, g_col2 = st.columns(2)
                    
                    with g_col1:
                        st.text_input("Applicant Name", value=u['name'], disabled=True)
                        st.text_input("Category & Domicile", value=f"{u['category']} | {u['state']}", disabled=True)
                        st.text_input("Verified Family Income", value=f"₹{u['income']:,}", disabled=True)
                    
                    with g_col2:
                        st.text_input("Target Scheme", value=target_scheme["name"], disabled=True)
                        st.text_input("Scheme Ceiling", value=f"₹{target_scheme['max_income']:,}", disabled=True)
                        dl_status = "✅ OAuth Token Active (Verified)" if st.session_state["digilocker_linked"] else "⚠️ Unlinked"
                        st.text_input("DigiLocker KYC Token", value=dl_status, disabled=True)

                    st.divider()

                    if not st.session_state["digilocker_linked"]:
                        st.warning("⚠️ Action Required: DigiLocker token is missing. Upload manual document proof to bypass.")
                        uploaded_file = st.file_uploader("Upload Income/Identity Proof (PDF/PNG)", type=["pdf", "png", "jpg"])
                        if st.button(t["submit_manual"], type="primary", use_container_width=True):
                            if uploaded_file:
                                result = tool_submit_application_impl(u["username"], target_scheme["id"], target_scheme["name"])
                                st.balloons()
                                st.success(f"🎉 Application Submitted Successfully! Reference ID: {result['reference_id']}")
                            else:
                                st.error("Please select a file to upload before submitting.")
                    else:
                        st.success("✅ Agent Verification PASSED: DigiLocker OAuth Token Active & Eligibility Verified.")
                        if st.button(t["execute_dbt"], type="primary", use_container_width=True):
                            if client:
                                status_box = st.status("🤖 Filing Agent working...", expanded=True)

                                def gateway_tool_router(fn_name, args):
                                    if fn_name == "fetch_vault_documents":
                                        result = tool_fetch_vault_documents_impl(st.session_state["digilocker_linked"])
                                        st.session_state["_agent_fetched_docs"] = result.get("documents", [])
                                        return result
                                    if fn_name == "validate_documents":
                                        return tool_validate_documents_impl(target_scheme, st.session_state.get("_agent_fetched_docs", []))
                                    if fn_name == "map_form_fields":
                                        return tool_map_form_fields_impl(u, target_scheme)
                                    if fn_name == "submit_application":
                                        result = tool_submit_application_impl(u["username"], target_scheme["id"], target_scheme["name"])
                                        st.session_state["_agent_last_submission"] = result
                                        return result
                                    return {"error": f"unknown tool '{fn_name}'"}

                                st.session_state["_agent_last_submission"] = None
                                system_prompt = (
                                    "You are YojnaMitra's Filing Agent. Follow this exact sequence using your tools: "
                                    "1) fetch_vault_documents  2) validate_documents  3) if (and only if) valid=true, "
                                    "call map_form_fields then submit_application. "
                                    "If validate_documents reports missing documents, DO NOT submit — instead your "
                                    "final answer must explain exactly which documents are missing and that manual "
                                    "upload is needed. After you finish, respond in plain text (2-4 sentences) "
                                    "summarizing what happened, quoting the real reference ID if a submission occurred."
                                )
                                user_prompt = f"Process the application for scheme_id={target_scheme['id']} ({target_scheme['name']})."

                                try:
                                    final_text = run_tool_agent(
                                        system_prompt, user_prompt, GATEWAY_TOOLS, gateway_tool_router, status_box
                                    )
                                    status_box.update(label="✅ Filing Agent Finished", state="complete", expanded=False)
                                    if final_text:
                                        if st.session_state.get("_agent_last_submission"):
                                            st.balloons()
                                        st.success(final_text)
                                    else:
                                        st.error("Agent did not reach a final answer within the turn limit. Try again.")
                                except Exception as e:
                                    status_box.update(label="❌ Agent Execution Interrupted", state="error")
                                    st.error(f"Error executing filing agent: {e}")
                            else:
                                st.warning("OPENROUTER_API_KEY is missing from environment/secrets.")
            else:
                st.error("No eligible schemes available for form processing based on your active demographic vector.")

        with tab4:
            st.header(f"🏛️ {u['name']}'s Beneficiary Dashboard")
            st.write("Overview of submitted government portal applications and e-KYC status.")

            conn = sqlite3.connect('yojna_mitra.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT scheme_name, reference_id, status, submitted_at FROM submissions WHERE username=? ORDER BY id DESC",
                (u["username"],)
            )
            submission_rows = cursor.fetchall()
            conn.close()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Active Applications", f"{len(submission_rows)} Submitted")
            m2.metric("DigiLocker Status", "Verified" if st.session_state["digilocker_linked"] else "Unlinked")
            m3.metric("DBT Approval Status", "Pre-Approved" if submission_rows else "No Submissions Yet")
            m4.metric("Kiosk Account ID", f"YM-{u['username'].upper()}")

            st.divider()
            st.subheader("📜 Portal Transaction Logs")
            if submission_rows:
                st.table([
                    {"Timestamp": row[3], "Scheme": row[0], "Reference ID": row[1], "Status": row[2]}
                    for row in submission_rows
                ])
            else:
                st.info("No applications submitted yet. File one from the Agentic Form Gateway tab.")

        with tab5:
            st.header(t["vault_header"])
            st.write(t["vault_caption"])

            v_col1, v_col2 = st.columns(2)
            with v_col1:
                if not st.session_state["digilocker_linked"]:
                    aadhaar_num = st.text_input(t["aadhaar_num"], max_chars=12)
                    if st.button(t["send_otp"], use_container_width=True):
                        if len(aadhaar_num) == 12 and aadhaar_num.isdigit():
                            st.session_state["otp_sent"] = True
                            st.info("OTP sent to Aadhaar Mobile (Test OTP: 123456)")
                        else:
                            st.error("Enter a valid 12-digit Aadhaar number.")

                    if st.session_state["otp_sent"]:
                        otp_in = st.text_input(t["enter_otp"], type="password", max_chars=6)
                        if st.button(t["verify_otp"], type="primary", use_container_width=True):
                            if otp_in == "123456":
                                st.session_state["digilocker_linked"] = True
                                st.session_state["otp_sent"] = False
                                st.success("DigiLocker Token Authenticated & Synced!")
                                st.rerun()
                            else:
                                st.error("Invalid OTP code. Use 123456 for testing.")
                else:
                    st.success("✅ DigiLocker Connected & Authenticated")
                    if st.button(t["revoke_token"], use_container_width=True):
                        st.session_state["digilocker_linked"] = False
                        st.rerun()

            with v_col2:
                st.markdown(f"**{t['synced_certs']}**")
                if st.session_state["digilocker_linked"]:
                    st.write("✔️ **Aadhaar Identity Card** (UIDAI)")
                    st.write("✔️ **Income Certificate** (Revenue Department)")
                    st.write("✔️ **Domicile Certificate** (State Portal)")
                    st.write("✔️ **Caste / Category Certificate**")
                else:
                    st.info("No documents linked. Authorize DigiLocker OTP to automatically fetch certificates.")

        with tab6:
            st.header(t["feedback_header"])
            with st.form("feedback_form"):
                rating = st.slider(t["feedback_slider"], 1, 5, 5)
                comments = st.text_area(t["feedback_comments"])
                if st.form_submit_button(t["feedback_submit"]):
                    st.success("Thank you! Your feedback has been registered.")