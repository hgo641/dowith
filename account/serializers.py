from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ('provider', 'uid', 'point', )
        extra_kwargs = {
            'password': {'write_only': True},
        }