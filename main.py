import ast
import json
import os
import re
from decimal import Decimal
from uuid import UUID

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
from Utilityfunctions import Iutility
import logging

DB = DB_config()
Cutility = Iutility()
# FastAPI app
app = FastAPI()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)
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



def get_user(username_or_email: str, db: Session):
    logging.info(f"Getting user for: {username_or_email}")
    user = DB.get_user_by_username_or_email(db, username_or_email)
    logging.info(f"User found: {user}")
    return user

# Serializer for generating and verifying session tokens
serializer = URLSafeTimedSerializer(SECRET)





@app.post("/insert-data/")
async def insert_data_endpoint(user_data: UM.UserData, db: Session = Depends(DB.get_db)):
    response_data = {}
    try:
        logging.info("Insert Data   -   Starting..")
        result = DB.get_user_by_username_or_email(db, user_data.username or user_data.email)
        if result:
            logging.info("User Already exists.")
            response_data = {
                "response_body": {"msg": "User already exists"},
                "status_code": 502  # Assuming existing_record is updated
            }
        else:
            hash_password = pwd_context.hash(user_data.password_hash)
            user_data.password_hash = hash_password
            DB.insert_data_into_db(user_data)
            logging.info("Data Inserted Successfully.")
            response_data = {
                "response_body": {"msg": "User Data Inserted Sucessfully."},
                "status_code": 100  # Assuming existing_record is updated
            }
        return UM.response_body(**response_data)

    except SQLAlchemyError as Err:
        response_data = {
            "response_body": {"msg": f"Failed to insert data into database: {Err}"},
            "response_code": 500,  # Assuming existing_record is updated
            "error_code":500
        }
        logging.info(json.dumps(response_data,indent=2))
        return UM.response_body(**response_data)


@app.post("/login/")
async def login_user(user_login: UM.userlogin, response: Response, db: Session = Depends(DB.get_db)):
    logging.info(f"Login attempt for: {user_login.username or user_login.email}")
    user = get_user(user_login.username or user_login.email, db)
    if not user:
        logging.info("Invalid credentials: user not found")
        response_data = {
            "response_body": {"msg": f"Invalid credentials"},
            "response_code": 400,  # Assuming existing_record is updated
            "error_code": 400
        }
        logging.info(f"Response: {response_data} ")
        return UM.response_body(**response_data)


    try:
        pwd_context.verify(user.password_hash,user_login.password_hash)
    except InvalidHashError:
        print("Invalid hash error")
        response_data = {
            "response_body": {"msg": f"Invalid password hash"},
            "response_code": 400,  # Assuming existing_record is updated
            "error_code": 400
        }
        return UM.response_body(**response_data)

    except VerifyMismatchError:
        logging.info("Password mismatch")
        response_data = {
            "response_body": {"msg": f"Invalid password hash"},
            "response_code": 400,  # Assuming existing_record is updated
            "error_code": 400
        }
        return UM.response_body(**response_data)

    global sessions
    sessions[user.username] = user  # Store user in session
    session_token = serializer.dumps(user.username,salt=SECRET)  # Generate session token
    logging.info(f"Session token generated: {session_token}")
    response.set_cookie(manager.cookie_name, session_token, httponly=True)
    DB.update_last_login(db, user.user_id)
    response_data = {
        "response_body": {"msg": f"Login Successfully"},
        "response_code": 200,  # Assuming existing_record is updated
        "error_code": 0
    }
    return UM.response_body(**response_data)

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

    session_token = request.cookies.get(manager.cookie_name)
    print(f"Accessing protected route with session token: {bool(session_token)}")
    if session_token:
        try:
            print("under try block")
            username = serializer.loads(session_token, salt=SECRET, max_age=1800)  # 30-minute expiration
            print(f"Loaded username from token: {username}")
            user = sessions.get(username)
            if user:
                print(f"User found in session: {user}")
                return {"message": f"After login msg Welcome {user.username}","code":"100"}
        except (BadSignature, SignatureExpired):
            print("Invalid signature")
            pass
    raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/add_fund")
async def add_fund_amount(request:Request,response: Response,User_balance : UM.UserBalance,db: Session = Depends(DB.get_db)):
    try:
        logging.info("under add fund Module.")
        updated_balance = 0
        session_token = request.cookies.get(manager.cookie_name)
        if session_token:
            logging.info("User Already Logged-in")
            username = serializer.loads(session_token, salt=SECRET, max_age=1800)  # 30-minute expiration
            user = sessions.get(username)
            user_email = DB.get_user_by_username_or_email(db,str(user))

            data_str = str(user)
            uuid_str = Cutility.get_uuid_str(data_str)
            fetch_balance = DB.balance_by_uuid(db,uuid_str)
            User_balance.prev_balance = fetch_balance
            User_balance.user_id = uuid_str

            if fetch_balance is None:
                fetch_balance = 0
            logging.info(f'Fetch balance {fetch_balance}')

            # print('histiory',uuid_str,fetch_balance,User_balance)
            if User_balance.order_type == "Deposit":
                logging.info(f"User deposit - {User_balance}")
                User_balance.user_id = uuid_str
                updated_balance = Decimal(fetch_balance) + Decimal(User_balance.order_amount)
                logging.info(f"updated amount -  {updated_balance}")
                User_balance.clr_balance = updated_balance
                DB.add_fund(User_balance)

            elif User_balance.order_type == "Withdrawl":
                logging.info(f"User Withdrawl - {User_balance}")

                if User_balance.order_amount < fetch_balance:
                    raise HTTPException(status_code=400, detail="Insufficient balance")
                else:
                    updated_balance = fetch_balance - User_balance.order_amount
                    User_balance.clr_balance = updated_balance
                    DB.withdrawl_transaction()
            else:
                print("Nothing",User_balance.order_type)
        else:
            response_data = {
                "response_body": {"msg": f"Un-Authorized"},
                "response_code": 400,  # Assuming existing_record is updated
                "error_code": 0
            }
            return response_data
            logging.info(json.dumps(response_data,indent=2))


    except Exception as Err:
        logging.info(f"Something went wrong {Err}")
        response_data = {
            "response_body": {"msg": f"something went wrong {Err}"},
            "response_code": 400,  # Assuming existing_record is updated
            "error_code": 0
        }
        return response_data



@app.post("/user_buy_coin")
async def fnCoin_purchase(request:Request,ORD:UM.order,db:Session=Depends(DB.get_db)):
    try:
        response_data = {}
        session_token = request.cookies.get(manager.cookie_name)
        if session_token:
            logging.info("User Already Logged-in")
            username = serializer.loads(session_token, salt=SECRET, max_age=1800)  # 30-minute expiration
            user = sessions.get(username)
            data_str = str(user)
            User_id = Cutility.get_uuid_str(data_str)
            fetch_balance = DB.balance_by_uuid(db, User_id)

            coin_code = ORD.coin_name
            Request_coin_qty = ORD.coin_qty
            coin_info_obj = DB.fnGet_coin_price_byname(coin_code)
            coin_id, coin_code, stock_coin_qty, coin_price = coin_info_obj.coin_id, coin_info_obj.coin_code, coin_info_obj.listed_qty, coin_info_obj.coin_price

            if Request_coin_qty > stock_coin_qty or Request_coin_qty<=0:
                logging.info(f"Requesting qty - {Request_coin_qty} is more than stock qty - {stock_coin_qty}")
                response_data = {
                    "response_body": {"msg": f"Bad Request"},
                    "response_code": 400,  # Assuming existing_record is updated
                    "error_code": 0
                 }
            else:
                amount = Request_coin_qty * coin_price
                if fetch_balance < amount:
                    print(fetch_balance, amount)
                    logging.info(f"Requested amount - {amount} is greater than user balance - {fetch_balance}")
                    response_data = {
                        "response_body": {"msg":f"Requested amount - {amount} is greater than user balance - {fetch_balance}"},
                        "response_code": 400,  # Assuming existing_record is updated
                        "error_code": 0
                    }

                else:
                    logging.info("User balance is updating")
                    customer_clr_balance = Decimal(fetch_balance) - Decimal(amount)
                    logging.info(f"User balance is updated - {customer_clr_balance}")

                    stock_coin_qty = stock_coin_qty - Request_coin_qty
                    logging.info(f'customer clr bal - {customer_clr_balance}')
                    #update customer stock
                    DB.fnupdate_customer_stock(coin_price,
                                               coin_id,
                                               User_id,
                                               coin_code,
                                               Request_coin_qty,
                                               customer_clr_balance,
                                               amount,
                                               "buy")
                    logging.info(f"Customer Database Updated")

                    response_data = {
                        "response_body": {"msg": f"Coin Purchased Successfully."},
                        "response_code": 400,  # Assuming existing_record is updated
                        "error_code": 0
                    }

        else:
            response_data = {
                "response_body": {"msg": f"Invalid Session"},
                "response_code": 400,  # Assuming existing_record is updated
                "error_code": 0
            }

        return response_data


    except Exception as err:
        response_data = {
            "response_body": {"msg": f"Invalid credentials: coin_code {err}"},
            "response_code": 400,  # Assuming existing_record is updated
            "error_code": 400
        }
        return UM.response_body(**response_data)

        #update stock coin qty
@app.post("/user_sell_coin")
async def fncoin_sell(request:Request,ORD:UM.order,db:Session=Depends(DB.get_db)):
    session_token = request.cookies.get(manager.cookie_name)
    if session_token:
        logging.info("User Already Logged-in")
        username = serializer.loads(session_token, salt=SECRET, max_age=1800)  # 30-minute expiration
        user = sessions.get(username)
        data_str = str(user)
        User_id = Cutility.get_uuid_str(data_str)

        coin_code = ORD.coin_name
        Request_coin_qty = ORD.coin_qty
        Request_price = ORD.coin_price

        sell_validation = DB.fnget_cx_stock_info(User_id,coin_code,Request_coin_qty)

        if sell_validation:
            if Request_coin_qty <= sell_validation.coin_qty:
                coin_info_obj = DB.fnGet_coin_price_byname(coin_code)
                curr_coin_price = coin_info_obj.coin_price
                if Request_price <= curr_coin_price:
                    sell_amount = curr_coin_price * Request_coin_qty
                    #update coin stock and customer stock
                else:
                    print("print que to move and wait for the order to excute when price match")
        else:
            response_data = {
                "response_body": {"msg": f"Bad Request"},
                "response_code": 400,  # Assuming existing_record is updated
                "error_code": 400
            }
            return UM.response_body(**response_data)


#---------------------------------------Admin Section ------------------------------------------#

@app.post("/add_stock_coin")
async def add_coin(request:Request,response:Response,CM:UM.coin_stock,db: Session = Depends(DB.get_db)):
    response_data = {}
    try:
        session_token = request.cookies.get(manager.cookie_name)
        if session_token:
            print("User Already Logged-in")
            username = serializer.loads(session_token, salt=SECRET, max_age=1800)  # 30-minute expiration
            user = sessions.get(username)
            user_email = DB.get_user_by_username_or_email(db, str(user))
            data_str = str(user)
            uuid_str = Cutility.get_uuid_str(data_str)
            is_admin,is_active = DB.is_active_admin(uuid_str)

            if Cutility.con_add_validation(CM.coin_qty,CM.coin_code):
                if is_active and is_admin:
                    DB.fnadd_coin(CM)
                    logging.info(f"{CM.coin_code} Coin Added Successfully @{CM.coin_price} Quantity {CM.coin_qty}")
                elif not is_active:
                    logging.info(f"Error Occured. User Activate Status : {is_active} ")
                    raise HTTPException(status_code=422, detail="Un-Authorized")
                elif not is_admin:
                    logging.info(f"Error Occured. User Admin Status : {is_admin} ")
                    raise HTTPException(status_code=422, detail="Un-Authorized")

            else:
                response_data = {
                    "response_body": {"msg": f"Bad Request. Coin qty Invalid: {CM.coin_qty}"},
                    "response_code": 200,  # Assuming existing_record is updated
                    "error_code": 400
                }

                return response_data

        else:
            logging.info(f"Invalid Session. User might logged out.")
            raise HTTPException(status_code=422, detail="Un-Authorized. Bad signature.")

    except Exception as Err:
        response_data = {
            "response_body": {"msg": f"Bad Request {Err}"},
            "response_code": 400,  # Assuming existing_record is updated
            "error_code": 400
        }
        return UM.response_body(**response_data)




