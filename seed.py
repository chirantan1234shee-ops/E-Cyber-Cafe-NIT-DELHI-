# seed.py
from database import SessionLocal, engine, Base, Scheme

Base.metadata.create_all(bind=engine)

def seed_schemes():
    db = SessionLocal()
    if db.query(Scheme.id).first():
        db.close()
        return

    schemes = [
        Scheme(
            name="PM Kisan Samman Nidhi",
            category="Agriculture",
            description="Income support of ₹6,000 per year to landholding farmers.",
            rules={"min_age": 18, "max_age": 100, "max_income": 500000.0, "allowed_states": ["All"], "eligible_categories": ["Farmer", "All"]},
            is_active=True
        ),
        Scheme(
            name="Uttar Pradesh Matritva Sahyog Yojana",
            category="Women & Child Welfare",
            description="Financial support for pregnant mothers in UP.",
            rules={"min_age": 19, "max_age": 45, "max_income": 200000.0, "allowed_states": ["Uttar Pradesh"], "eligible_categories": ["Female", "Mother"]},
            is_active=True
        )
    ]
    db.add_all(schemes)
    db.commit()
    db.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed_schemes()