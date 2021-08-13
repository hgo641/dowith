from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', "is_active", "is_admin", "is_superuser", "is_staff",)
        read_only_fields = ('provider', 'uid', 'point', )
