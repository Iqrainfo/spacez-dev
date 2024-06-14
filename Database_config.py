from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from Models import User_models as UM
from contextlib import contextmanager
import requests
import os
class DB_config:

    def __init__(self):
        self.DATABASE_URL = os.environ.get("PLSQL_URL")
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.engine = None

    def init_db_conn(self):
        self.DATABASE_URL = self.fnPSQL_token()
        # print('hell',self.DATABASE_URL)
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)



    @contextmanager
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_user_by_username_or_email(self,db, login):
        with self.SessionLocal() as db:
            # print(login)
            sql = text("SELECT user_id, username, email, password_hash FROM users WHERE username = :login OR email = :login")
            return db.execute(sql, {"login": login}).fetchone()

    def update_last_login(self,db, user_id):
        with self.SessionLocal() as db:
            sql = text("UPDATE users SET last_login = NOW() WHERE user_id = :user_id")
            db.execute(sql, {"user_id": user_id})
            db.commit()


    def insert_data_into_db(self,data: UM.UserData):
        with self.SessionLocal() as db:
            # Construct the SQL INSERT statement
            sql = text(
                "INSERT INTO users (username, email, password_hash, mobile_number, identity_card_no, issuing_authority, kyc_done, id_created_on, created_at, updated_at, last_login) "
                "VALUES (:username, :email, :password_hash, :mobile_number, :identity_card_no, :issuing_authority, :kyc_done, :id_created_on, :created_at, :updated_at, :last_login)"
            )
            # Execute the SQL statement with values from the UserData object
            db.execute(sql, {
                "username": data.username,
                "email": data.email,
                "password_hash": data.password_hash,
                "mobile_number": data.mobile_number,
                "identity_card_no": data.identity_card_no,
                "issuing_authority": data.issuing_authority,
                "kyc_done": data.kyc_done,
                "id_created_on": data.id_created_on,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
                "last_login": data.last_login
            })
            db.commit()
