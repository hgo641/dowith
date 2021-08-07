from rest_framework import serializers
from .models import *
from account.serializers import *
import datetime


class ChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = "__all__"
        read_only_fields = ('captain', )


class GatheringChallengeSerializer(serializers.ModelSerializer):

    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = "__all__"
        read_only_fields = ('captain', )

    def get_days_left(self, obj):
        return (obj.start_date - datetime.date.today()).days