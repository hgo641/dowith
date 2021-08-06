import datetime
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import *


class ChallengeView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):

        gathering_challenge = Challenge.objects.filter(start_date__gt=datetime.date.today())
        gathering_serializer = ChallengeSerializer(gathering_challenge, many=True)

        ongoing_challenge = Challenge.objects.filter(start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today())
        ongoing_serializer = ChallengeSerializer(ongoing_challenge, many=True)

        complete_challenge = Challenge.objects.filter(end_date__lt=datetime.date.today())
        complete_serializer = ChallengeSerializer(complete_challenge, many=True)

        return_data = {
            "gathering": gathering_serializer.data,
            "ongoing": ongoing_serializer.data,
            "complete": complete_serializer.data
        }

        return Response(return_data)

    def post(self, request):

        serializer = ChallengeSerializer(data=request.data)

        if serializer.is_valid():

            if not request.user.is_authenticated:
                return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

            serializer.save(captain=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChallengeDetailView(APIView):
    def get(self, request, pk):
        pass
