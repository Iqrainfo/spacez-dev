from fastapi import FastAPI, HTTPException, Depends,Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from Database_config import *
import Database_config as DB

# from Models import UserData

# FastAPI app
app = FastAPI()
pwd_context = PasswordHasher()



# FastAPI endpoint to insert data into the database
@app.post("/insert-data/")
async def insert_data_endpoint(user_data: UM.UserData,db: Session = Depends(get_db)):
    try:
        result = get_user_by_username_or_email(db, user_data.username or user_data.email)
        if result:
            return {"message": "User already exists","Error_code":"502"}

        print('before call', user_data.password_hash)
        # Hash the password
        hash_password = pwd_context.hash(user_data.password_hash)
        # Assign the hashed password to user_data
        user_data.password_hash = hash_password
        print('After call', hash_password, user_data.password_hash)

        DB.insert_data_into_db(user_data)
        return {"message": "Data inserted successfully"}
    except SQLAlchemyError as e:
        # If an error occurs during insertion, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail=f"Failed to insert data into database: {e}")

def verify_password(plain_password, hashed_password):
    print(plain_password,hashed_password)
    if plain_password == hashed_password:
        return True
    # return pwd_context.verify(plain_password, hashed_password)



@app.post("/login/")
async def login_user(user_login: UM.userlogin, db: Session = Depends(get_db)):
    try:
        # Fetch user by username or email
        result = get_user_by_username_or_email(db, user_login.username or user_login.email)
        print(result)
        if result:
            user_id, username, email, password_hash = result
            if verify_password(user_login.password_hash, password_hash):
                # Optionally update last login timestamp
                update_last_login(db, user_id)
                return {"message": "Login successful", "user_id": user_id, "username": username, "email": email}
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            raise HTTPException(status_code=404, detail="Invalid credentials")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to login: {e}")


@app.get("/")
async def index():
    return {"message": "Welcome to API 2.0"}
