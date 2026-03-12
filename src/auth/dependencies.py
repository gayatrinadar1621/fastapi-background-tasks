from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from fastapi import status, Depends
from src.auth.utils import verify_jwt_token

access_token_scheme = HTTPBearer()

def get_current_user(credentials=Depends(access_token_scheme)):
    print("Credentials received -->",credentials)
    token = credentials.credentials
    payload = verify_jwt_token(token)
    print("payload from get_current_user ===========>", payload)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Token")
    
    return payload

def required_role(role:str):
    print("IN REQUIRED ROLEEE", role)
    def check_role(user=Depends(get_current_user)):
        print("Inside check role function yayy... role list -->", role)
        print("user for checking roles", user)
        print(user["user"]["role"])
        incoming_role_from_request = user["user"]["role"]
        account_verified = user["user"]["is_verified"]
        if not account_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email first")
        if incoming_role_from_request != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have enough privilege to view this")
    return check_role
