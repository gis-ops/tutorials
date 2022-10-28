from datetime import datetime, timedelta

import jwt


def create_token(user: str, refresh: bool = False) -> str:
    minutes = (
        30
        if not refresh
        else 60 * 24
    )
    expires_delta = datetime.utcnow() + timedelta(minutes=minutes)

    to_encode = {"exp": expires_delta, "sub": user}
    encoded_jwt = jwt.encode(to_encode, "SUPER_SECRET_KEY", algorithm="HS256")

    return encoded_jwt
