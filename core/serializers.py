from rest_framework import serializers
from .models import *
from account.serializers import *
import datetime


class ChallengeSerializer(serializers.ModelSerializer):

    participated_count = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = "__all__"
        read_only_fields = ('captain', )

    def get_participated_count(self, obj):
        return Participation.objects.filter(challenge=obj).count()


class ParticipationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participation
        fields = "__all__"
        read_only_fields = ('user', 'challenge', 'life_left', )


class GatheringChallengeSerializer(serializers.ModelSerializer):

    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = "__all__"
        read_only_fields = ('captain', )

    def get_days_left(self, obj):
        return (obj.start_date - datetime.date.today()).days


class VerificationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Verification
        fields = "__all__"


class VerificationSerializer(serializers.ModelSerializer):

    author = serializers.SerializerMethodField()

    class Meta:
        model = Verification
        fields = "__all__"
        read_only_fields = ("participation_id", "create_at", 'is_reported', )

    def get_author(self, obj):

        user = obj.participation_id.user
        serializer = UserSerializer(user)

        return serializer.data


class ChallengeDetailSerializer(serializers.ModelSerializer):

    challenge_status = serializers.SerializerMethodField()
    participated_count = serializers.SerializerMethodField()
    total_challenge_period = serializers.SerializerMethodField()
    elapsed_days = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()
    captain_name = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = "__all__"
        read_only_fields = ('captain', )


    def get_captain_name(self, obj):
        return obj.captain.nickname

    def get_challenge_status(self, obj):
        if obj.start_date <= datetime.date.today() <= obj.end_date:
            return "ongoing"
        elif datetime.date.today() < obj.start_date:
            return "gathering"
        else:
            return "finished"

    def get_participated_count(self, obj):
        return Participation.objects.filter(challenge=obj).count()

    def get_total_challenge_period(self, obj):
        return (obj.end_date - obj.start_date).days

    def get_elapsed_days(self, obj):
        if obj.start_date <= datetime.date.today():
            return (datetime.date.today() - obj.start_date).days + 1
        else:
            return 0

    def get_days_left(self, obj):
        return (obj.start_date - datetime.date.today()).days
