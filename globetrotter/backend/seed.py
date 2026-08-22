import json
from backend.database import SessionLocal
from backend.models.city import City
from backend.models.activity import Activity

def seed_database():
    db = SessionLocal()
    
    # 1. Seed Cities
    with open("backend/seed_data/cities.json", "r") as f:
        cities = json.load(f)
        for c in cities:
            # Check if it already exists to prevent duplicates
            if not db.query(City).filter(City.id == c["id"]).first():
                db.add(City(**c))
                
    # 2. Seed Activities
    with open("backend/seed_data/activities.json", "r") as f:
        activities = json.load(f)
        for a in activities:
            if not db.query(Activity).filter(Activity.id == a["id"]).first():
                db.add(Activity(**a))
                
    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()