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
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()