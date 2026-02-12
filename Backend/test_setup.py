"""Quick script to create a test user and verify APIs work."""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:123456789@localhost:5432/Commet"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Insert a test user
    conn.execute(text("INSERT INTO users (username) VALUES ('test_user_1') ON CONFLICT DO NOTHING"))
    conn.commit()

    # Check the user
    rows = conn.execute(text("SELECT id, username FROM users LIMIT 5")).fetchall()
    print("Users:", rows)
    if rows:
        print(f"Test user ID: {rows[0][0]}")
