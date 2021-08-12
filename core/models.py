from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


User = settings.AUTH_USER_MODEL


class Challenge(models.Model):
    title = models.CharField(max_length=20, null=False, blank=False)
    thumbnail_url = models.ImageField(null=False, blank=False)
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

    def __str__(self):
        return str("사용자 {}가 참여하는 {} 챌린지".format(self.user, self.challenge))


class Verification(models.Model):
    participation_id = models.ForeignKey(Participation, on_delete=models.PROTECT)
    file_url = models.FileField(null=False, blank=False)
    article = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verificated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.participation_id)