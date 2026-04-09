import uvicorn
from dotenv import load_dotenv
import multiprocessing
cpu_count = multiprocessing.cpu_count()
print(f"CPU Count: {cpu_count}")
workers = cpu_count * 2 + 1
# load_dotenv()
# host  = os.getenv("HOST")
# print(f"Server running on {host}")
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        reload=True,
        host="localhost",
        port=9000
    )