from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.auth.models import CreateUserModel, UserAuthModel, LoginUserModel, UpdateModel
from fastapi.exceptions import HTTPException
from fastapi import status
from src.auth.utils import hash_password, verify_password, create_jwt_token
import uuid
from datetime import timedelta
from src.auth.utils import create_url_safe_token, decode_url_safe_token
from src.mail import mail, create_message
from src.config import Config
from src.celery_tasks import send_mail

class Service:
    async def is_user_exists(self, email:str, session:AsyncSession):
        statement = select(UserAuthModel).where(UserAuthModel.email == email)
        result = await session.execute(statement)
        user_present = result.scalar_one_or_none()
        return user_present
    
    async def create_user(self, user_data:CreateUserModel, session:AsyncSession):
        existing_user = await self.is_user_exists(user_data.email, session)
        print("existing_user", existing_user)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        
        # add user to database
        user_dict = user_data.model_dump()
        newuser = UserAuthModel(**user_dict)
        newuser.password = hash_password(user_dict["password"])

        session.add(newuser)
        await session.commit()
        await session.refresh(newuser)

        # send verification email
        email_token = create_url_safe_token({"email":newuser.email})
        url_link = f"http://{Config.DOMAIN}/verifymail/{email_token}"
        subject = "Verify Your Email"
        html_message = f"""
            <h2> Verify Your Email </h2>
            <p> Please click on this <a href="{url_link}"> link </a> to verify your email.</p>
        """ 
       
        send_mail.delay(
            recipients=[newuser.email],
            subject=subject,
            body=html_message
        )
        
        return {
            "message":"Account has been created, please check your email to verify your account.",
            "user":newuser
        }
    
    async def user_login(self, user_data:LoginUserModel, session:AsyncSession):
        existing_user = await self.is_user_exists(user_data.email, session)
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
        print("existing_user", existing_user)
        print("existing_user type", type(existing_user))
        is_valid_user = verify_password(user_data.password, existing_user.password)
        print("is_valid_user",is_valid_user)
        if not is_valid_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Credentials")
        
        # user is valid, so create access token
        access_token = create_jwt_token(user_data={
            "user_id":existing_user.id , 
            "email":existing_user.email, 
            "role":existing_user.role,
            "is_verified":existing_user.is_verified
        })
        print("Created token -->", access_token)

        # user is valid, so create refresh token and store in redis database
        # refresh_token = str(uuid.uuid4())
        # await store_refresh_token(
        #     refresh_token,
        #     existing_user.id,
        #     existing_user.email,
        #     timedelta(days=7)
        # )
        
        return {
            "message":"Login successful",
            "access_token" : access_token,
            "user_details" : {"user_id":existing_user.id, "email":existing_user.email, "role":existing_user.role}
        }
    
    async def update_user(self, userid:str, user:UpdateModel, session:AsyncSession):
        userid = int(userid)
        print("type of userid", userid, type(userid))
        user_to_update = await session.get(UserAuthModel, userid)
        print("user_to_update",user_to_update)
        if not user_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found to update")
        user_dict = user.model_dump(exclude_unset=True)
        for k,v in user_dict.items():
            setattr(user_to_update,k,v)
        await session.commit()
        return user_to_update

    async def delete_user(self, userid:str, session:AsyncSession):
        userid = int(userid)
        user_to_delete = await session.get(UserAuthModel, userid)
        print("user_to_delete",user_to_delete)
        if not user_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found to delete")
        await session.delete(user_to_delete)
        await session.commit()
        return {"message":f"User with ID {userid} deleted successfully"}

    async def get_user_by_email(self, email:str, session:AsyncSession):
        statement = select(UserAuthModel).where(UserAuthModel.email==email)
        res = await session.execute(statement)
        return res.scalar_one_or_none()

    async def verify_mail(self, token:str, session:AsyncSession):
        data = decode_url_safe_token(token)
        print("decoded data", data)
        print("email decoded data", data["email"])
        email = data["email"]
        if not email:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occurred during verification")
        user_present = await self.get_user_by_email(email, session)
        print("user present", user_present)
        if not user_present:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        update_dict = UpdateModel(is_verified=True)
        await self.update_user(user_present.id, update_dict, session)

        return {
            "message" : "Email have been verified successfully!"
        }

        
        

