import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Construct DATABASE_URL from individual environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        print("✅ Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

def drop_db_and_tables():
    confirm = os.getenv("CONFIRM_DROP", "no")
    if confirm.lower() != "yes":
        print("Operación cancelada.")
        return
    
    try:
        SQLModel.metadata.drop_all(engine)
        print("✅ Tables dropped successfully.")
    except Exception as e:
        print(f"Error dropping tables: {e}")

def get_session():
    with Session(engine) as session:
        yield session

