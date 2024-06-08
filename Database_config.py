from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from Models import User_models as UM
from contextlib import contextmanager

# Database connection
# DATABASE_URL = "postgresql://postgres:123456@localhost/spacez"  # Update with your actual connection string
DATABASE_URL = "postgresql://userinfo_hw9w_user:TC1WKWwBUxv4eqyziCTfeXDQJ6081ht7@dpg-cpdoprv109ks73el94jg-a.oregon-postgres.render.com:5432/userinfo_hw9w"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
engine = None


def start():
    try:
        DATABASE_URL = "postgres://userinfo_hw9w_user:TC1WKWwBUxv4eqyziCTfeXDQJ6081ht7@dpg-cpdoprv109ks73el94jg-a.oregon-postgres.render.com/userinfo_hw9w"  # Update with your actual connection string
        engine = create_engine(DATABASE_URL)
    except Exception as Err:
        print(Err)

# start()




@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username_or_email(db, login):
    with SessionLocal() as db:
        sql = text("SELECT user_id, username, email, password_hash FROM users WHERE username = :login OR email = :login")
        return db.execute(sql, {"login": login}).fetchone()

def update_last_login(db, user_id):
    with SessionLocal() as db:
        sql = text("UPDATE users SET last_login = NOW() WHERE user_id = :user_id")
        db.execute(sql, {"user_id": user_id})
        db.commit()



def insert_data_into_db(data: UM.UserData):
    with SessionLocal() as db:
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