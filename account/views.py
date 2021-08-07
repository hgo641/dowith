from .models import *
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import *


# Create your views here.

class UserView(APIView):
    def get(self, request, pk):

        serializer = UserSerializer(request.user)
        if request.user.id is pk:
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
