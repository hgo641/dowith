import jwt
import os
from datetime import datetime, timedelta
from django.conf import settings

ACCESS_TOKEN_EXPIRES_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRES", "60")
REFRESH_TOKEN_EXPIRES_DAYS = os.environ.get("REFRESH_TOKEN_EXPIRES", "365")


def generateAccessToken(user):
    aud = ["urn:dowith:user"]
    return jwt.encode(
        {
            "iss": "urn:dowith",
            "sub": str(user.id),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRES_MINUTES)),
            "aud": aud,
            "type": "access",
            "provider": user.provider,
            "nickname": user.nickname,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )


def generateRefreshToken(user, request, refresh):
    user_agent = request.META.get("HTTP_USER_AGENT")
    x_real_ip = request.META.get("HTTP_X_REAL_IP")
    ip = ""
    if x_real_ip:
        ip = x_real_ip
    else:
        ip = request.META.get("REMOTE_ADDR")
    print(ip)
    refresh.device = user_agent
    refresh.ip = ip
    refresh.last_refreshed = datetime.utcnow()
    refresh.user = user
    refresh.save()
    return jwt.encode(
        {
            "iss": "urn:dowith",
            "sub": str(refresh.id),
            "iat": refresh.last_refreshed,
            "exp": refresh.last_refreshed + timedelta(days=int(REFRESH_TOKEN_EXPIRES_DAYS)),
            "type": "refresh",
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
