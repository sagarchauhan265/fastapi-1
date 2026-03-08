from fastapi import FastAPI
from app.config.settings import settings
from app.config.db import check_db_connection,Base,engine
import app.models
# from dotenv import load_dotenv
# import os
# load_dotenv()
# title = os.getenv("TITLE")
# version = os.getenv("API_VERSION")
from app.api.api import main_router
app = FastAPI(
    title=settings.TITLE,
    version=settings.API_VERSION,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    # docs=None   
)



@app.on_event("startup")
def startup_event():
    if check_db_connection():  
        print("✅ Database connected successfully")
    else:
        print("❌ Database connection error")


Base.metadata.create_all(bind=engine)
app.include_router(main_router,prefix="/api/v1")



        


