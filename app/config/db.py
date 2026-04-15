from sqlalchemy import create_engine, text 
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.config.settings import settings

print(f"Database URL: {settings.DB_URL}")
DATABASE_URL = (settings.DB_URL)
engine = create_engine(DATABASE_URL,echo=False,max_overflow=0, pool_size=10, pool_timeout=30, pool_recycle=1800)  # Adjust pool settings as needed
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.execute(text("CREATE DATABASE IF NOT EXISTS ecom"))
            # connection.execute(text("ALTER TABLE category ADD COLUMN updated_at DateTime after created_at"))
            # connection.execute(text("ALTER TABLE category ADD COLUMN create_by varchar(100) after updated_at"))
            # connection.execute(text("ALTER TABLE products ADD COLUMN currency varchar(10) after cat_id"))
        return True
    except SQLAlchemyError as e:
        print("❌ Database connection failed:", e)
        return False
    


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
