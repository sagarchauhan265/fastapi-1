import uvicorn;
from dotenv import load_dotenv
import os
load_dotenv()
host  = os.getenv("HOST")
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=host,
        port=8000
    )