from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import HTTPException, Depends, status
from jose import jwt, JWTError

security = HTTPBearer()
SECRET_KEY = 'django-insecure-8agvt%#ebkgv22evn9!flk3o(629!$=*(sv*b1d44acew6h)vo'
algorithm = "HS256"


def get_current_user(
        credential: HTTPAuthorizationCredentials = Depends(security)
):
    print("fetching token...")
    token = credential.credentials
    print(f"Fetched token {token}")
    print("Using this token, decoding the auth payload and fetch the current user id..")
    try:
        payload = jwt.decode(token=token, algorithms=algorithm, key=SECRET_KEY)
        user_id = payload.get("user_id")
        print(f"User_id => {user_id}")
        if not user_id:
            raise HTTPException(status_code=401, detail="invalid token")

        print(f"auth payload =>{payload}")
        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )