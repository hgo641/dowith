import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from account.models import User


class JWTAuthentication(BaseAuthentication):

    """
    AUTHORIZATION : Bearer mdopNQ3r1039rh109hr193h1r3.asmdmqwpondq.nfewewanf (예)
    """

    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return None
        try:
            token = token.split(' ')
            if token[0] != 'Bearer':
                return None
            token = token[1]
            print(token)
            access_data = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms="HS256",
                audience="urn:dowith:user",
                issuer="urn:dowith"
            )
            id = access_data.get('sub')
            user = User.objects.get(id=id)
            return (user, None)
        except (ValueError, jwt.exceptions.DecodeError):
            return None
        except:
            return None
