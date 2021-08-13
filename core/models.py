import datetime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from uuid import uuid4
from django.utils import timezone



User = settings.AUTH_USER_MODEL



def set_challenge_image_name(instance, filename):
    return "image/challenge/{}/{}/{}/{}.jpg".format(datetime.datetime.today().year,
                                                    datetime.datetime.today().month,
                                                    datetime.datetime.today().day,
                                                    uuid4().hex)

def set_verification_image_name(instance, filename):
    return "image/verification/{}/{}/{}/{}.jpg".format(datetime.datetime.today().year,
                                                    datetime.datetime.today().month,
                                                    datetime.datetime.today().day,
                                                    uuid4().hex)

class Challenge(models.Model):
    title = models.CharField(max_length=20, null=False, blank=False)
    thumbnail_url = models.FileField(null=True, blank=True, upload_to=set_challenge_image_name)
    create_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    fee = models.PositiveIntegerField(null=False, blank=False)
    captain = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.title)


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    challenge = models.ForeignKey(Challenge, on_delete=models.PROTECT)
    total_distribute_charge = models.PositiveIntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return str("사용자 {}가 참여하는 {} 챌린지".format(self.user, self.challenge))


class Verification(models.Model):

    participation_id = models.ForeignKey(Participation, on_delete=models.PROTECT)
    image_url = models.ImageField(null=True, blank=True, upload_to=set_verification_image_name)
    article = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    is_verificated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.participation_id)