from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password',)
        read_only_fields = ('provider', 'uid', 'point', )
