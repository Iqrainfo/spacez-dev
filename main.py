from fastapi import FastAPI, HTTPException, Depends,Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from Database_config import *
from Database_config import DB_config
DB = DB_config()
# from Models import UserData

# FastAPI app
app = FastAPI()
pwd_context = PasswordHasher()



# FastAPI endpoint to insert data into the database
@app.post("/insert-data/")
async def insert_data_endpoint(user_data: UM.UserData,db: Session = Depends(DB.get_db)):
    try:
        result = DB.get_user_by_username_or_email(db, user_data.username or user_data.email)
        if result:
            return {"message": "User already exists","Error_code":"502"}


        hash_password = pwd_context.hash(user_data.password_hash)
        DB.insert_data_into_db(user_data)
        return {"message": "Data inserted successfully"}
    except SQLAlchemyError as e:
        # If an error occurs during insertion, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail=f"Failed to insert data into database: {e}")


@app.post("/login/")
async def login_user(user_login: UM.userlogin, db: Session = Depends(DB.get_db)):
    try:
        # Fetch user by username or email
        result = DB.get_user_by_username_or_email(db, user_login.username or user_login.email)
        if result:
            user_id, username, email, password_hash = result
            print('ok', user_login.password_hash)

            password_hashed = pwd_context.hash(user_login.password_hash)
            DB.update_last_login(db, user_id)
            return {"message": "Login successful", "code":"100"}

        else:
            raise HTTPException(status_code=404, detail="Invalid credentials")

    except VerifyMismatchError:
        return {"message": "Login Failed","code":"404"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to login: {e}")


@app.get("/")
async def index():
    return {"message": "Welcome to API 3.0"}
