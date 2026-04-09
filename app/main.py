from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware 
from app.config.settings import settings
from app.config.db import check_db_connection,Base,engine
import app.models
from fastapi.middleware.gzip import GZipMiddleware

# from dotenv import load_dotenv
# import os
# load_dotenv()
# title = os.getenv("TITLE")
# version = os.getenv("API_VERSION")
from app.api.api import main_router
bearer_scheme = HTTPBearer()

app = FastAPI(
    title=settings.TITLE,
    version=settings.API_VERSION,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    # docs=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allows all origins
    allow_credentials=False,
    allow_methods=["*"],      # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],      # Allows all headers
)

@app.on_event("startup")
def startup_event():
    if check_db_connection():  
        print("✅ Database connected successfully")
    else:
        print("❌ Database connection error")

app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses larger than 1000 bytes
Base.metadata.create_all(bind=engine)
app.include_router(main_router,prefix="/api/v1")



        


