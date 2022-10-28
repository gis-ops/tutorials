from functools import lru_cache

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlmodel import Session, select
from starlette.requests import Request

from engine import engine
from models import Users


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class Authorizer(HTTPBearer):
    def __init__(self, auto_error=True):
        super(Authorizer, self).__init__(auto_error=auto_error)
        self.user = None

    async def __call__(self, request: Request):
        creds: HTTPAuthorizationCredentials = await super(Authorizer, self).__call__(request)
        if not creds or not creds.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

        if not (token := self.verify_jwt(creds.credentials)):
            raise HTTPException(status_code=403, detail="Invalid token or expired token.")

        self.user = token.sub
        return self

    @staticmethod
    def verify_jwt(jwtoken):
        try:
            payload = jwt.decode(
                jwtoken,
                "SUPER_SECRET_KEY",
                algorithms=["HS256"],
            )
            return TokenPayload(**payload)
        except Exception:
            return False

    def get_user_info(self):
        return get_user_info(self.user)


@lru_cache
def get_user_info(username):
    with Session(engine) as session:
        postal_code = session.exec(
            select(Users.plz).where(Users.username == username)
        ).first()

        return postal_code
