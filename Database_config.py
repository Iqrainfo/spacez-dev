from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from Models import User_models as UM
from contextlib import contextmanager
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
class DB_config:

    def __init__(self):
        self.DATABASE_URL = os.getenv("PLSQL_URL")
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db_conn(self):
        self.DATABASE_URL = self.fnPSQL_token()
        print('hell',self.DATABASE_URL)
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    # def fnPSQL_token(self):
    #
    #     # Your HCP API token
    #     hcp_api_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InByaXZhdGU6YzRjY2RlMWMtNGIzMy00YjMxLTkyZjEtNTQ4ZjY3YmRlMmNkIiwidHlwIjoiSldUIn0.eyJhdWQiOlsiaHR0cHM6Ly9hcGkuaGFzaGljb3JwLmNsb3VkIl0sImF6cCI6IkxVVm5wU0RUaXdMZXlPWFc1bHNleXJqRjJCRlc4eGlTIiwiZXhwIjoxNzE3OTQ5MjQ5LCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJodHRwczovL2Nsb3VkLmhhc2hpY29ycC5jb20vcHJpbmNpcGFsLXR5cGUiOiJzZXJ2aWNlIiwiaWF0IjoxNzE3OTQ1NjQ5LCJpc3MiOiJodHRwczovL2F1dGguaWRwLmhhc2hpY29ycC5jb20vIiwianRpIjoiOGQ3NGM3NjYtMGJjZi00Mzk1LTkyMzAtYzk2Yzk5ODJmM2FlIiwibmJmIjoxNzE3OTQ1NjQ5LCJzdWIiOiJzZWNyZXRzLXNhbXBsZS1hcHAtMTcxNzkyNzI1ODUzOC03MjY2OThAMGI0N2NjZTUtNGFjOC00MWFmLTk3ZmYtNzFkMTgxYmY5MDVlIn0.A4Y2uiac_4mwV-vHvPJXWFvdIhsDV7vurfNqclUtt2vvmcL7-blRuUtxdWMFuUiqncFH5cD1IcdW2m1gB1YVXqRUiQlJ_lM5bjuQb6AAF1ga_GhWScjJLjGle1HOLQSTBO733G18BWG5klG_9S01UfjGdDgA9g_B-oHomEfT4gSzj5uFlvi8nxye6q7NGOLRiFFS2m-OzYldumaAP_AO1xd63Dq6R4QCPGouDSHnMfy8JC3Dy1MdnFkKom-5ulTxPnikgyem6Pnd-wIp-fyb_-wy4M4HrCFk7_sGKumOz2TnG8UGLo8LakwiI5wR9y_NBpYT_HI2DagYdwEabVGk9V5TjKARtJHiWBEJuYKqWU1wKUQ3_tbONMNXVPFUdvMh_tYO1d7X3il3WMF3j2yZ6AyEPj-LS3aUUlXix9yOEkCnoJWiPvTmnsDvCm-CIijAqoe7SEjasSz5_PMm2MZt0tE5RBzkVewxTDcRtFhQqcdvpd8rAQ7x4sPTN6zeZt3-sqFac0FYdnuVN_i4TXsJIwU3AbPgd3dST6soeBHPd9fj3mVtOnt5pGgiXJocrSQBGp3nTgeiGZnkUWGyfCiJ1k0sLFJBb_VRbNlivshbTQjW03z7XqUIYCfwPmtsE17J8T1UfO1lx_6BxieM6pEvauvFwjczwQRVIntTuEH8L7Q"
    #     # Set the API endpoint URL (replace with the actual endpoint you want to access)
    #     api_url = "https://api.cloud.hashicorp.com/secrets/2023-06-13/organizations/f155217a-501e-4d1a-b977-f11bf7a87d02/projects/0b47cce5-4ac8-41af-97ff-71d181bf905e/apps/sample-app/open"
    #
    #     headers = {
    #         "Authorization": f"Bearer {hcp_api_token}",
    #         "Content-Type": "application/json"
    #     }
    #     response = requests.get(api_url, headers=headers)
    #     if response.status_code == 200:
    #         print("Request was successful!")
    #         response_data = response.json()
    #         url =(response_data['secrets'][1]['version']['value'])
    #         print('hi',url)
    #         return url
    #     else:
    #         print(f"Request failed with status code {response.status_code}")


    @contextmanager
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_user_by_username_or_email(self,db, login):
        with self.SessionLocal() as db:
            print(login)
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