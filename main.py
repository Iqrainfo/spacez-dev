import os
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from Database_config import *
from Database_config import DB_config
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi.middleware.cors import CORSMiddleware

DB = DB_config()

# FastAPI app
app = FastAPI()

#To handle cors error

origins = [
    os.environ.get("Allowed_Api")
    # os.getenv("Allowed_Api")
]


# Add CORS middleware to your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



SECRET = os.urandom(24).hex()  # A random secret key for the login manager

pwd_context = PasswordHasher()
manager = LoginManager(SECRET, token_url='/login/', use_cookie=True)
manager.cookie_name = 'auth_cookie'

sessions = {}

@manager.user_loader
def load_user(username: str):
    print(f"Loading user: {username}")
    user = sessions.get(username)
    print(f"User found in sessions: {user}")
    return user

def get_user(username_or_email: str, db: Session):
    print(f"Getting user for: {username_or_email}")
    user = DB.get_user_by_username_or_email(db, username_or_email)
    print(f"User found: {user}")
    return user

# Serializer for generating and verifying session tokens
serializer = URLSafeTimedSerializer(SECRET)

@app.post("/insert-data/")
async def insert_data_endpoint(user_data: UM.UserData, db: Session = Depends(DB.get_db)):
    try:
        result = DB.get_user_by_username_or_email(db, user_data.username or user_data.email)
        if result:
            return {"message": "User already exists", "Error_code": "502"}

        hash_password = pwd_context.hash(user_data.password_hash)
        user_data.password_hash = hash_password
        DB.insert_data_into_db(user_data)
        return {"message": "Data inserted successfully"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert data into database: {e}")

@app.post("/login/")
async def login_user(user_login: UM.userlogin, response: Response, db: Session = Depends(DB.get_db)):
    print(f"Login attempt for: {user_login.username or user_login.email}")
    user = get_user(user_login.username or user_login.email, db)
    if not user:
        print("Invalid credentials: user not found")
        raise InvalidCredentialsException

    try:
        pwd_context.verify(user.password_hash,user_login.password_hash)
    except InvalidHashError:
        print("Invalid hash error")
        raise HTTPException(status_code=400, detail="Invalid password hash")
    except VerifyMismatchError:
        print("Password mismatch")
        raise InvalidCredentialsException

    global sessions
    sessions[user.username] = user  # Store user in session
    session_token = serializer.dumps(user.username)  # Generate session token
    print(f"Session token generated: {session_token}")
    response.set_cookie(manager.cookie_name, session_token, httponly=True)
    DB.update_last_login(db, user.user_id)
    return {"message": "Login successful", "code": "100"}

@app.post("/logout/")
async def logout_user(request: Request, response: Response):
    session_token = request.cookies.get(manager.cookie_name)
    print(f"Logout attempt with session token: {session_token}")
    if session_token:
        try:
            username = serializer.loads(session_token)
            print(f"Loaded username from token: {username}")
            sessions.pop(username, None)  # Remove user from session store
        except BadSignature:
            print("Bad signature in session token")
            pass
        response.delete_cookie(manager.cookie_name)
    return {"message": "Logout successful"}

@app.get("/")
async def index():
    return {"message": "Welcome to API 3.0"}

@app.get("/protected/")
async def protected_route(request: Request):
    print(f"hi")

    session_token = request.cookies.get(manager.cookie_name)
    print(f"Accessing protected route with session token:")
    if session_token:
        try:
            username = serializer.loads(session_token, salt=SECRET, max_age=1800)  # 30-minute expiration
            print(f"Loaded username from token: {username}")
            user = sessions.get(username)
            if user:
                print(f"User found in session: {user}")
                return {"message": f"Welcome {user.username}","code":"100"}
        except (BadSignature, SignatureExpired):
            print("Invalid signature")
            pass
    raise HTTPException(status_code=401, detail="Unauthorized")
