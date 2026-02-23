from fastapi import FastAPI
from dotenv import load_dotenv
import os
load_dotenv()
title = os.getenv("TITLE")
version = os.getenv("API_VERSION")
from app.api.api import main_router
app = FastAPI(
    title=title,
    version=version
)

app.include_router(main_router,prefix="/api/v1")
