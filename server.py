import uvicorn
from dotenv import load_dotenv
import os
# load_dotenv()
# host  = os.getenv("HOST")
# print(f"Server running on {host}")
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=9000
    )