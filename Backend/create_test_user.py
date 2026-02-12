from app import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Create a test user
    db.execute(text("INSERT INTO users (id, username) VALUES (999, 'TestPlayer') ON CONFLICT (id) DO NOTHING"))
    db.commit()
    print("User 999 created successfully.")
except Exception as e:
    print(f"Error creating user: {e}")
finally:
    db.close()
