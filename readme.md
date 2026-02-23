# CRAETE ENV
python -m venv fast
# ACTIVATE ENV
 fast/Scripts/Activate
# DEPENDENCY FILE
pip freeze > requirements.txt

# INSTALL MODULE
pip install fastapi
pip install uvicorn
pip install python-dotenv
pip install sqlalchemy
pip install mysql-connector
pip install python-multipart

# RUN UVICORN SERVER
uvicorn app.main:app --reload