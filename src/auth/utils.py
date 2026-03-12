from passlib.context import CryptContext
import jwt
from src.config import Config
from datetime import datetime, timedelta, timezone
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

password_context = CryptContext(
    schemes=['bcrypt'],
    deprecated="auto"  # it means in future, if bcrypt deprecates, use another more secure, non-deprecated algorithm instead. 
)

# hash password
def hash_password(password:str) -> str:
    return password_context.hash(password)

# verify client password with the hash present in the database
def verify_password(password:str, hash:str) -> bool:
    return password_context.verify(password, hash)

# create jwt token
def create_jwt_token(user_data:dict, expiry:timedelta = None):
    payload = {
        "user" : user_data,
        "iat" : datetime.now(tz=timezone.utc),
        "exp" : datetime.now(tz=timezone.utc) + (expiry if expiry is not None else timedelta(minutes=10)),
        "jti" : str(uuid.uuid4())  # unique id given to jwt token
    }

    token = jwt.encode(
        payload,
        key = Config.SECRET_KEY,
        algorithm = Config.ALGORITHM
    )
    return token

# verify jwt token
def verify_jwt_token(token:str):
    try:
        token_data = jwt.decode(
            token, 
            key = Config.SECRET_KEY,
            algorithms = [Config.ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None

    except Exception as e:
        logging.exception(e)
        return None

# ====================================================================================

# Email Verification Token setup

serializer = URLSafeTimedSerializer(
    secret_key=Config.SECRET_KEY,
    salt="email-configuration"
)

def create_url_safe_token(data:dict):
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token:str):
    try:
        data = serializer.loads(
            token,
            max_age=3600
        )
        return data
    except Exception as e:
        logging.error(str(e))




