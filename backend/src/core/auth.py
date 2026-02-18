from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

from src.schemas.user_info import UserInfo


security = HTTPBearer()


def is_authorized(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInfo:
    """
    Extracts user information from Microsoft access token.
    """

    token = credentials.credentials

    try:
        decoded = jwt.get_unverified_claims(token)

        user_id = decoded.get("oid")
        email = decoded.get("preferred_username") or decoded.get("upn")
        name = decoded.get("name")

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return UserInfo(
            user_id=user_id,
            email=email,
            name=name,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
