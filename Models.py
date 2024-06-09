from pydantic import BaseModel, EmailStr, model_validator, root_validator
from typing import Optional
from datetime import date, datetime

# Pydantic model for data validation
class User_models:

    class UserData(BaseModel):
        username: str
        email: EmailStr
        password_hash: str
        mobile_number: Optional[str] = "123456789"
        identity_card_no: str = None
        issuing_authority: str = None
        kyc_done: Optional[bool] = False
        id_created_on: Optional[date] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None
        last_login: Optional[datetime] = None


    class Update_Profile(BaseModel):
        username: str
        # email: EmailStr
        password_hash: str
        mobile_number: Optional[str]
        identity_card_no: str
        issuing_authority: str
        kyc_done: Optional[bool] = False
        last_profile_change: Optional[datetime] = None


    class userlogin(BaseModel):
        username: Optional[str]
        email: Optional[EmailStr]
        password_hash: str

        @root_validator(pre=True)
        def check_username_or_email(cls, values):
            username, email = values.get('username'), values.get('email')
            if username=="" and  email=="":
                raise ValueError('Either username or email must be provided')
            return values
