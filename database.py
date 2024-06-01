from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, EmailStr
from sqlalchemy import text

DATABASE_URL = "postgresql://postgres:123456@localhost/spacez"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
inspector = inspect(engine)

# Pydantic model for data validation
class UserData(BaseModel):
    username: str
    name: str
    docs_no: str
    docs_type: str
    email: EmailStr
    mobile: str
    address: str
    password: str

def table_exists(table_name):
    return table_name in inspector.get_table_names()

def create_table():
    if not table_exists('user_data'):
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE user_data (
                    uniqueid SERIAL PRIMARY KEY,
                    username VARCHAR(100),
                    name VARCHAR(100),
                    docs_no VARCHAR(100),
                    docs_type VARCHAR(100),
                    email VARCHAR(100),
                    mobile VARCHAR(100),
                    address VARCHAR(255),
                    password VARCHAR(100)
                )
            """))
        print("Table 'user_data' created successfully.")
    else:
        print("Table 'user_data' already exists.")

# database.py

def insert_data_into_db(data: UserData):
    try:
        create_table()  # Check and create the table if it doesn't exist
        db = SessionLocal()
        # Construct the SQL INSERT statement
        sql = text("INSERT INTO user_data (username, name, docs_no, docs_type, email, mobile, address, password) VALUES (:username, :name, :docs_no, :docs_type, :email, :mobile, :address, :password)")
        # Execute the SQL statement with values from UserData object
        db.execute(sql, {
            "username": data.username,
            "name": data.name,
            "docs_no": data.docs_no,
            "docs_type": data.docs_type,
            "email": data.email,
            "mobile": data.mobile,
            "address": data.address,
            "password": data.password
        })
        db.commit()
        db.close()
        return {"message": "Data inserted successfully"}
    except SQLAlchemyError as e:
        return {"error": f"Failed to insert data into database: {e}"}
