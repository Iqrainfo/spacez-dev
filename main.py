from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# FastAPI app
app = FastAPI()

# Database connection
DATABASE_URL = "postgresql://postgres:123456@localhost/spacez"  # Update with your actual connection string
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

# Function to insert data into the database
def insert_data_into_db(data: UserData):
    try:
        with SessionLocal() as db:
            # Construct the SQL INSERT statement
            sql = text("INSERT INTO user_data (username, name, docs_no, docs_type, email, mobile, address, password) "
                       "VALUES (:username, :name, :docs_no, :docs_type, :email, :mobile, :address, :password)")
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
    except SQLAlchemyError as e:
        # If an error occurs during insertion, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail=f"Failed to insert data into database: {e}")

# FastAPI endpoint to insert data into the database
@app.post("/insert-data/")
async def insert_data_endpoint(user_data: UserData):
    insert_data_into_db(user_data)
    return {"message": "Data inserted successfully"}


@app.get("/")

async def index():
    return {"message": "Welcome to API"}

