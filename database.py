import sqlite3

def init_db():
    conn = sqlite3.connect("yojna_mitra.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        full_name TEXT,
        password TEXT,
        income INTEGER,
        occupation TEXT,
        state TEXT,
        digilocker_verified INTEGER DEFAULT 0
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schemes (
        id TEXT PRIMARY KEY,
        title TEXT,
        ministry TEXT,
        income_ceiling INTEGER,
        target_group TEXT,
        benefits TEXT,
        portal_url TEXT
    )
    """)
    
    schemes = [
        ("PM_VIDYALAXMI", "PM-Vidyalaxmi Higher Education Loan", "Ministry of Education", 800000, "Student", "3% interest subvention on education loans up to ₹7.5 Lakhs.", "https://vidyalakshmi.co.in"),
        ("PM_KISAN", "PM-Kisan Samman Nidhi", "Ministry of Agriculture", 200000, "Farmer", "Direct income support of ₹6,000 per year in 3 equal installments.", "https://pmkisan.gov.in"),
        ("PMAY_U", "Pradhan Mantri Awas Yojana (Urban)", "Ministry of Housing", 600000, "Self-Employed", "Interest subsidy on home loans for first-time home buyers.", "https://pmaymis.gov.in")
    ]
    cursor.executemany("INSERT OR REPLACE INTO schemes VALUES (?, ?, ?, ?, ?, ?, ?)", schemes)
    conn.commit()
    conn.close()

def register_user(username, full_name, password, income, occupation, state):
    conn = sqlite3.connect("yojna_mitra.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, 0)", (username, full_name, password, income, occupation, state))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def verify_user(username, password):
    conn = sqlite3.connect("yojna_mitra.db")
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, income, occupation, state, digilocker_verified FROM users WHERE username = ? AND password = ?", (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"username": username, "full_name": row[0], "income": row[1], "occupation": row[2], "state": row[3], "digilocker_verified": row[4]}
    return None

def update_digilocker_status(username, status=1):
    conn = sqlite3.connect("yojna_mitra.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET digilocker_verified = ? WHERE username = ?", (status, username))
    conn.commit()
    conn.close()

def get_all_schemes():
    conn = sqlite3.connect("yojna_mitra.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, ministry, income_ceiling, target_group, benefits, portal_url FROM schemes")
    rows = cursor.fetchall()
    conn.close()
    schemes = []
    for r in rows:
        schemes.append({
            "id": r[0], "title": r[1], "ministry": r[2], "max_income": r[3],
            "target": r[4], "summary": r[5], "portal_url": r[6]
        })
    return schemes

def get_scheme_by_id(scheme_id):
    for s in get_all_schemes():
        if s["id"] == scheme_id:
            return s
    return {}