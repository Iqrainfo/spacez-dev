from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# FastAPI app
app = FastAPI()

# Database connection
DATABASE_URL = "postgresql://postgres:123456@localhost/spacez"  # Update with your actual connection string
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to insert data into the database
def insert_data_into_db():
    try:
        with SessionLocal() as db:
            # Construct the SQL INSERT statement
            sql = text("INSERT INTO user_data (username, name, docs_no, docs_type, email, mobile, address, password) "
                       "VALUES (:username, :name, :docs_no, :docs_type, :email, :mobile, :address, :password)")
            # Hardcoded values for simplicity
            values = {
                "username": "test_user",
                "name": "Test User",
                "docs_no": "12345",
                "docs_type": "Passport",
                "email": "test@example.com",
                "mobile": "1234567890",
                "address": "Test Address",
                "password": "test_password"
            }
            # Execute the SQL statement with hardcoded values
            db.execute(sql, values)
            db.commit()
    except SQLAlchemyError as e:
        # If an error occurs during insertion, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail=f"Failed to insert data into database: {e}")

# FastAPI endpoint to insert data into the database
@app.post("/insert-data/")
async def insert_data_endpoint():
    insert_data_into_db()
    return {"message": "Data inserted successfully"}
