from rest_framework import serializers
from .models import *
from account.serializers import *


class ChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = "__all__"
        read_only_fields = ('captain', )