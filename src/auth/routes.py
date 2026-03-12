from fastapi import APIRouter, status, Depends
from src.auth.models import CreateUserModel, UserAuthModel, LoginUserModel, EmailModel, UpdateModel
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.services import Service
from src.auth.dependencies import get_current_user, required_role
from src.mail import create_message, mail
from src.celery_tasks import send_mail

user_router = APIRouter()
auth_service = Service()

@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def user_signup(user_data:CreateUserModel, session:AsyncSession = Depends(get_session)):
    result = await auth_service.create_user(user_data, session)
    print("result", result)
    return result

@user_router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(user_data:LoginUserModel, session:AsyncSession = Depends(get_session)):
    result = await auth_service.user_login(user_data, session)
    print("result", result)
    return result

# dummy route to test protected route
@user_router.get("/dummy")
async def protected_dummy_route(user_details=Depends(get_current_user)):
    print("user_details",user_details)
    return {"message":"You are able to see this because you have been successfully authenticated.", "user_details":user_details}

# endpoint to allow access to admin only
@user_router.get("/admin")
async def admin_dashboard(user=Depends(required_role("ADMIN"))):
    print("Hello, this is admin dashboard")
    return {"message":"Hello, this is admin dashboard"}

# endpoint to allow access to user only
@user_router.get("/user")
async def user_dashboard(user=Depends(required_role("USER"))):
    print("Hello, this is user dashboard")
    return {"message":"Hello, this is user dashboard"}

# endpoint to test mail without background task
@user_router.post("/sendmail")
async def send_mail_normal(data:EmailModel):
    print("email from send mail endpoint", data.emailaddress)
    emails=data.emailaddress
    subject = "Mail Setup Testing"
    body = "<h2>Welcome to FastAPI Mail</h2>"
    message = create_message(
        recipients=emails,
        subject=subject,
        body=body
    )
    await mail.send_message(message)
    return {"message":"Email sent successfully"}


# endpoint to test mail with background task
@user_router.post("/sendmail_background")
async def send_mail_background  (data:EmailModel):
    print("email from send mail endpoint", data.emailaddress)
    emails=data.emailaddress
    subject = "Mail Setup Testing"
    body = "<h2>Welcome to FastAPI Mail</h2>"
    send_mail.delay(
        recipients=emails,
        subject=subject,
        body=body
    )
    return {"message":"Email sent successfully"}

# endpoint to update user details
@user_router.post("/update/{userid}", status_code=status.HTTP_200_OK)
async def update_user(userid:str, user:UpdateModel, session:AsyncSession = Depends(get_session)):
    print("type of userid", userid, type(userid))
    res = await auth_service.update_user(userid, user, session)
    return res

# endpoint to delete a user
@user_router.delete("/delete/{userid}", status_code=status.HTTP_200_OK)
async def delete_user(userid:str, session:AsyncSession = Depends(get_session)):
    res = await auth_service.delete_user(userid, session)
    return res

# endpoint to verify email
@user_router.get("/verifymail/{token}")
async def verify_mail(token:str, session:AsyncSession = Depends(get_session)):
    print("Inside verifying email route >>>>")
    res = await auth_service.verify_mail(token, session)
    return res

