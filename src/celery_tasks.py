from celery import Celery
from src.mail import mail, create_message
from asgiref.sync import async_to_sync
import asyncio
c_app = Celery()

c_app.config_from_object("src.config")

# creating a task

@c_app.task()
def send_mail(recipients:list[str], subject:str, body:str):
    try:
        message = create_message(recipients, subject, body)
        print("message", message)
        async_to_sync(mail.send_message)(message)
        print("Email sent!!!")
    except Exception as e:
        print("oops error", str(e))



