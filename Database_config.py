import time
from datetime import date
from http.client import HTTPException
from typing import Optional
import traceback

from sqlalchemy import create_engine, text, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from Models import User_models as UM
from contextlib import contextmanager
import requests
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class CoinStock(Base):
    __tablename__ = 'coin_stock'
    coin_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    coin_code = Column(String, index=True)
    coin_price = Column(Float)
    listed_qty = Column(Integer)
    created_on = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserInfo(Base):
    __tablename__ = 'users'
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String)
    email = Column(String)
    password_hash = Column(String)
    mobile_number = Column(String)
    identity_card_no = Column(String)
    issuing_authority = Column(String)
    kyc_done = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserBalance(Base):
    __tablename__ = 'user_balance'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id =  Column(UUID(as_uuid=True))
    prev_balance = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    order_type = Column(String)
    order_amount = Column(Float)
    clr_balance = Column(Float)

class customer_coin_stock(Base):
    __tablename__ = 'Customer_coin_stock'
    last_transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True))
    coin_id = Column(UUID(as_uuid=True))
    coin_code = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    coin_qty = Column(String)
    Average_buying_price = Column(Float)



class coin_stock_transaction(Base):
    __tablename__ = 'coin_Stock_Transactions'
    Transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    coin_id = Column(UUID(as_uuid=True))
    coin_code = Column(String, index=True)
    coin_price = Column(Float)
    listed_qty = Column(Integer)
    created_on = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    order_type = Column(String)


class customer_transactions(Base):
    __tablename__ = 'transactions'
    transaction_id =  Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    transaction_type = Column(String)
    order_type = Column(String)
    amount = Column(Float)
    coin_code = Column(Float)
    price = Column(Float)
    quantity = Column(Integer)
    payment_method = Column(String)
    fee_amount = Column(Float)
    fee_currency = Column(String)
    transaction_status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_at =Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True))
    clr_balance = Column(Float)


class DB_config:

    def __init__(self):
        self.DATABASE_URL = os.environ.get("PLSQL_URL")
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.engine = None

    def init_db_conn(self):
        self.DATABASE_URL = self.fnPSQL_token()
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @contextmanager
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    def is_active_admin(self,uuid):
        print("unser is active admin")
        with self.SessionLocal() as db:
            sql = text("SELECT is_active, is_admin FROM users WHERE user_id=:uuid")
            result = db.execute(sql,{"uuid":uuid})
            row = result.fetchone()
            return row

    def get_user_by_username_or_email(self,db, login):
        with self.SessionLocal() as db:
            print(login)
            sql = text("SELECT user_id, username, email, password_hash FROM users WHERE username = :login OR email = :login")
            return db.execute(sql, {"login": login}).fetchone()

    def balance_by_uuid(self,db,id):
        with self.SessionLocal() as db:
            sql = text("Select clr_balance from user_balance where user_id=:id")
            result = db.execute(sql,{"id":id})
            row = result.fetchone()
            if row is not None:
                balance = row[0]  # Access the first column in the row
                # print(f"User balance: {balance}")
                return balance
            else:
                print("No balance found for the user")
    def update_last_login(self,db, user_id):
        with self.SessionLocal() as db:
            sql = text("UPDATE users SET last_login = NOW() WHERE user_id = :user_id")
            db.execute(sql, {"user_id": user_id})
            db.commit()

    def insert_data_into_db(self,data: UM.UserData):
        response_data = {}
        try:
            with self.SessionLocal() as db:
                # Construct the SQL INSERT statement
                # sql = text(
                #     "INSERT INTO users (username, email, password_hash, mobile_number, identity_card_no, issuing_authority, kyc_done, id_created_on, created_at, updated_at, last_login) "
                #     "VALUES (:username, :email, :password_hash, :mobile_number, :identity_card_no, :issuing_authority, :kyc_done, :id_created_on, :created_at, :updated_at, :last_login)"
                # )
                # Execute the SQL statement with values from the UserData object
                User_info = UserInfo(
                    username = data.username,
                    email = data.email,
                    password_hash = data.password_hash,
                    mobile_number = data.mobile_number,
                    identity_card_no = data.identity_card_no,
                    issuing_authority = data.issuing_authority,
                    kyc_done = data.kyc_done,
                    created_at = data.created_at,
                    updated_at = data.updated_at,
                    last_login = data.last_login
                )


                db.add(User_info)
                db.commit()
                db.refresh(User_info)
                # response_data = {
                #     "response_body":{"msg" :"User Data Inserted Sucessfully."},
                #     "status_code": 100  # Assuming existing_record is updated
                # }

        except Exception as Err:
            print(f"Something went wrong... {Err}")
            response_data = {
                "response_body": {"msg":f"Error occured {Err}"},
                "response_code": 400  # Assuming existing_record is updated
            }

            db.rollback()
            return UM.response_body(**response_data)

    def add_fund(self,data:UM.UserBalance):
        try:
            with self.SessionLocal() as db:
                # Check if the record exists
                existing_record = db.query(UserBalance).filter(UserBalance.user_id == data.user_id).with_for_update().first()


                if existing_record:
                    # Update the existing record
                    existing_record.prev_balance = data.prev_balance
                    existing_record.updated_at = data.updated_at or datetime.now()
                    existing_record.order_type = data.order_type
                    existing_record.order_amount = data.order_amount
                    existing_record.clr_balance = data.clr_balance
                    db.commit()
                    db.refresh(existing_record)
                    return {"message": "Balance updated successfully", "balance": existing_record}
                else:
                    # Insert a new record
                    print('new record insert',data.order_amount,data.prev_balance)
                    user_balance = UserBalance(
                        user_id=data.user_id,
                        prev_balance = 0,
                        updated_at=data.updated_at or datetime.now(),
                        order_type=data.order_type,
                        order_amount = data.order_amount,
                        clr_balance = data.order_amount
                    )
                    db.add(user_balance)
                    db.commit()
                    db.refresh(user_balance)
                    return {"message": "Balance added successfully", "balance": user_balance}
        except Exception as Err:
            db.rollback()
            print(f"message : {Err}")

    def withdrawl(self,data:UM.UserBalance):
        pass
    def buy_coin(self,data:UM.order):
        pass

    def fnGet_coin_price_byname(self,coin_code):

        with self.SessionLocal() as db:
            coin = db.query(CoinStock).filter(CoinStock.coin_code == coin_code).with_for_update().first()
            if not coin:
                raise HTTPException(status_code=404, detail="Coin not found")
            return coin
    def fnget_cx_stock_info(self,user_id,coin_code,coin_qty):
        with self.SessionLocal() as db:
            existing_record = db.query(customer_coin_stock).filter(customer_coin_stock.user_id == user_id,
                                                                   customer_coin_stock.coin_code == coin_code,
                                                                   customer_coin_stock.coin_qty >= coin_qty).with_for_update().first()

            if not existing_record:
                raise HTTPException(status_code=404, detail="Coin not found")
            else:
                return existing_record



    #Buy sell Portion Customer
    def fnupdate_customer_stock(self,
                                coin_price,
                                coin_id,
                                user_id,
                                coin_code,
                                add_coin_qty,
                                customer_clr_balance,
                                amount,
                                order_type):

        print('coin_code',coin_code)
        try:
            with self.SessionLocal() as db:
                print("before filter")
                unique_id = uuid.uuid4()

                #user stock update
                existing_record = db.query(customer_coin_stock).filter(customer_coin_stock.user_id == user_id,customer_coin_stock.coin_id == coin_id).with_for_update().first()
                print("after filter")

                if not existing_record and order_type=='buy':
                    print("New  record")
                    User_stock_update = customer_coin_stock(
                        last_transaction_id=unique_id,
                        user_id = user_id,
                        coin_id = coin_id,
                        coin_code = coin_code,
                        coin_qty = add_coin_qty,
                        Average_buying_price = coin_price
                    )
                    db.add(User_stock_update)


                    # db.commit()
                    # db.refresh(User_stock_update)
                elif order_type == 'buy':
                    print("Existing  record",existing_record.coin_code,coin_code)
                    existing_record.coin_qty = existing_record.coin_qty + add_coin_qty,
                    existing_record.Average_buying_price=(existing_record.Average_buying_price + coin_price) / 2
                    # existing_record.coin_code = coin_code
                    # db.commit()
                    # db.refresh(existing_record)
                # db.commit()
                elif order_type == 'sell':
                    print("Existing  record", existing_record.coin_code, coin_code)
                    existing_record.coin_qty = existing_record.coin_qty - add_coin_qty,
                    # existing_record.Average_buying_price = (existing_record.Average_buying_price + coin_price) / 2
                    # existing_record.coin_code = coin_code


                #update customer balance
                user_balance_query = db.query(UserBalance).filter(UserBalance.user_id == user_id).with_for_update().first()
                if user_balance_query:
                    user_balance_query.id = unique_id
                    user_balance_query.prev_balance = user_balance_query.clr_balance
                    user_balance_query.clr_balance = customer_clr_balance
                    # db.commit()
                    # db.refresh(user_balance_query)



                #update stock manager
                stock_manager_query = db.query(CoinStock).filter(CoinStock.coin_id == coin_id).with_for_update().first()
                if stock_manager_query:
                    if order_type=='buy':
                        stock_manager_query.last_transaction_id = unique_id
                        stock_manager_query.listed_qty = stock_manager_query.listed_qty - add_coin_qty
                        stock_manager_query.last_updated = datetime.utcnow()
                        # db.commit()
                        #
                    elif order_type=='sell':
                        stock_manager_query.last_transaction_id = unique_id
                        stock_manager_query.listed_qty = stock_manager_query.listed_qty + add_coin_qty
                        stock_manager_query.last_updated = datetime.utcnow()



                #insert stock_manager_transactions

                stock_manager_transaction = coin_stock_transaction(
                    coin_id = coin_id,
                    Transaction_id = unique_id,
                    coin_code   =  coin_code,
                    coin_price  =   coin_price,
                    listed_qty  =   add_coin_qty,
                    created_on  =   stock_manager_query.created_on,
                    created_by  =   user_id,
                    last_updated=   datetime.utcnow(),
                    order_type  =   order_type
                )
                db.add(stock_manager_transaction)

                #insert transactions
                transaction_update = customer_transactions(
                transaction_id =  unique_id,
                transaction_type = order_type,
                order_type = f"{order_type}/crypto",
                amount = amount,
                coin_code = coin_code,
                price = coin_price,
                quantity = add_coin_qty,
                payment_method = "Wallet",
                fee_amount = 0,
                fee_currency = "INR",
                transaction_status = "Success",
                created_at = datetime.utcnow(),
                updated_at =datetime.utcnow(),
                user_id = user_id,
                clr_balance = customer_clr_balance
                )

                db.add(transaction_update)




                db.commit()
                db.refresh(User_stock_update)
                db.refresh(stock_manager_query)
                db.refresh(user_balance_query)
                db.refresh(transaction_update)

                print("committed sucesssfully")

        except Exception as err:
            db.rollback()
            print(f"error occured {err}")
            tb = traceback.format_exc()
            # Print the error message and the traceback
            print(f"Error occurred: {err}")
            print(f"Traceback:\n{tb}")

    #--------------------------------Admin Tasks------------------------------------------#

    def fnadd_coin(self,data:UM.coin_stock):
        try:
            with self.SessionLocal() as db:
                db_coin_stock = CoinStock (
                    coin_code = data.coin_code,
                    coin_price = data.coin_price,
                    listed_qty = data.coin_qty,
                    created_on = data.adding_date,
                    created_by = data.last_added_by,
                    last_updated = data.last_updated
                )
                db.add(db_coin_stock)
                db.commit()
                db.refresh(db_coin_stock)

                return {"message": "Coin added successfully"}
        except Exception as Err:
            # db.rollback()
            return {"message": f"{Err}"}



