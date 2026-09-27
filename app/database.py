import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# For local dev this defaults to a SQLite file (zero setup).
# For deployment, set DATABASE_URL to your Postgres connection string
# (e.g. from Supabase / Neon / Render) and it switches automatically.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pms.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
