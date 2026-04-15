from pydantic_settings import BaseSettings
# from pydantic import Field

class Settings(BaseSettings):
# SERVER CONFIG
    API_VERSION:str
    TITLE:str="Hello"
    BASE_URL:str
    HOST:str
    PORT:int
# DATABASE CONFIG MYSQL
    DB_NAME:str
    DB_HOST:str
    DB_USER:str
    DB_PASSWORD:str
    DB_PORT:int
    DB_URL:str

# SECERET 
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
# CLOUDINARY CONFIG
    CLOUDINARY_CLOUD_NAME:str
    CLOUDINARY_API_KEY:str
    CLOUDINARY_API_SECRET:str
# RAZORPAY CONFIG
    RAZORPAY_KEY_ID:str
    RAZORPAY_KEY_SECRET:str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()