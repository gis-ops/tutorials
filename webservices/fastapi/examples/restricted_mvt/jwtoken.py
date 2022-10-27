from datetime import datetime, timedelta

import jwt


def create_token(user: str, expires_delta: timedelta = None, refresh: bool = False) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        minutes = (
            30
            if not refresh
            else 60 * 24
        )
        expires_delta = datetime.utcnow() + timedelta(minutes=minutes)

    to_encode = {"exp": expires_delta, "sub": user}
    encoded_jwt = jwt.encode(to_encode, "SUPER_SECRET_KEY", algorithm="HS256")

    return encoded_jwt
