from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import uuid


# Create your models here.
datetime.utcnow()

def set_user_image_name(instance, filename):
    return "image/user/{}/{}/{}/{}.jpg".format(datetime.datetime.today().year,
                                                    datetime.datetime.today().month,
                                                    datetime.datetime.today().day,
                                                    uuid.uuid4().hex)

class UserManager(BaseUserManager):

    def create_user(self, provider, uid, nickname, image_url=None):

        user = self.model(
            provider=provider,
            uid=uid,
            nickname=nickname,
            image_url=image_url
        )

        user.save(using=self._db)
        return user

    def create_superuser(self, uid, nickname, password=None):
        user = self.create_user(
            provider='admin',
            uid=uid,
            nickname=nickname,
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    objects = UserManager()

    provider = models.CharField(max_length=10, null=False, blank=False)
    uid = models.CharField(max_length=20, null=False, blank=False, unique=True)
    password = models.CharField(_('password'), max_length=128, null=True, blank=True)
    nickname = models.CharField(max_length=10, null=False, blank=False)
    registered_on = models.DateTimeField(auto_now_add=True)
    image_url = models.ImageField(null=True, blank=True, upload_to=set_user_image_name)
    point = models.PositiveIntegerField(null=False, blank=False, default=5000)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'uid'
    REQUIRED_FIELDS = ['nickname']


class RefreshToken(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, null=False, blank=False
    )
    last_refreshed = models.DateTimeField(
        default=datetime.utcnow, null=False, blank=False
    )
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
        null=False,
        blank=False,
    )
    device = models.CharField(max_length=300, null=True, blank=True)
    ip = models.GenericIPAddressField(
        unpack_ipv4=True, protocol="both", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
