# CRAETE ENV
python -m venv fast
# ACTIVATE ENV
 fast/Scripts/Activate
# DEPENDENCY FILE
pip freeze > requirements.txt

pip install -r requirements.txt. # if already have requirments.txt
# INSTALL MODULE
pip install fastapi
pip install uvicorn
pip install python-dotenv
pip install sqlalchemy
pip install mysql-connector or pip install pymysql
pip install python-multipart
pip install pydantic-settings
pip install passlib # FOR encryption

# RUN UVICORN SERVER    
uvicorn app.main:app --reload

# DB CONNECTION URL
#DATABASE URL
postgresql+psycopg://user:pass@localhost:5432/dbname
mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}


<!-- DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
) -->

# PACKAGES
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.12.1
click==8.3.1
colorama==0.4.6
fastapi==0.129.0
greenlet==3.3.2
h11==0.16.0
idna==3.11
mysql-connector-python==9.6.0
pydantic==2.12.5
pydantic-settings==2.13.1
pydantic_core==2.41.5
python-dotenv==1.2.1
python-multipart==0.0.22
SQLAlchemy==2.0.47
starlette==0.52.1
typing-inspection==0.4.2
typing_extensions==4.15.0
uvicorn==0.40.0


Create Login,Registration API- 