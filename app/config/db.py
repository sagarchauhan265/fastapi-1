from sqlalchemy import create_engine, text 
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.config.settings import settings

print(f"Database URL: {settings.DB_URL}")
DATABASE_URL = (settings.DB_URL)
engine = create_engine(DATABASE_URL,echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            
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



