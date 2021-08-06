from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


User = settings.AUTH_USER_MODEL


class Challenge(models.Model):
    title = models.CharField(max_length=20, null=False, blank=False)
    thumbnail_url = models.URLField()  # 나중에 기본 썸네일 추가 예정
    create_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    fee = models.PositiveIntegerField(null=False, blank=False)
    life = models.PositiveSmallIntegerField(null=False, blank=False)
    captain = models.ForeignKey(User, on_delete=models.PROTECT)


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.PROTECT)
    life_left = models.PositiveSmallIntegerField(null=False, blank=False)


class Verification(models.Model):
    participation_id = models.ForeignKey(Participation, on_delete=models.CASCADE)
    file_url = models.URLField()
    article = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_reported = models.BooleanField(default=False)