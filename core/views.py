import datetime
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import *
from .tasks import dowith_duhee


class ChallengeMainView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):

        gathering_challenge = Challenge.objects.filter(start_date__gt=datetime.date.today())
        gathering_serializer = ChallengeSerializer(gathering_challenge, many=True)

        ongoing_challenge = Challenge.objects.filter(start_date__lte=datetime.date.today(),
                                                     end_date__gte=datetime.date.today())
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


class ChallengeTodayView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        ongoing_challenge = Challenge.objects.filter(participation__user=request.user,
                                                     participation__verification=None)
        finished_challenge = Challenge.objects.filter(participation__user=request.user,
                                                      participation__verification=not None)

        ongoing_serializer = ChallengeSerializer(ongoing_challenge, many=True)
        finished_serializer = ChallengeSerializer(finished_challenge, many=True)

        return_data = {
            "ongoing": ongoing_serializer.data,
            "finished": finished_serializer.data
        }

        return Response(return_data)


class ChallengeMyView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        participated_challenge = Challenge.objects.filter(participation__user=request.user)
        participated_ongoing_challenge = participated_challenge.filter(start_date__lte=datetime.date.today(),
                                                                       end_date__gte=datetime.date.today())

        participated_ongoing_serializer = ChallengeSerializer(participated_ongoing_challenge, many=True)

        finished_challenge = participated_challenge.filter(end_date__lt=datetime.date.today())
        finished_serializer = ChallengeSerializer(finished_challenge, many=True)

        gathering_challenge = participated_challenge.filter(start_date__gt=datetime.date.today())
        gathering_serializer = GatheringChallengeSerializer(gathering_challenge, many=True)

        return_data = {
            "gathering_ongoing_count": gathering_challenge.count() + participated_ongoing_challenge.count(),
            "finished_count": finished_challenge.count(),
            "gathering": gathering_serializer.data,
            "ongoing": participated_ongoing_serializer.data,
            "finished": finished_serializer.data
        }

        return Response(return_data)


class ChallengeDetailView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            challenge = Challenge.objects.get(pk=pk)
            serializer = ChallengeDetailSerializer(challenge)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):

        if not Challenge.objects.filter(pk=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        participation = Participation.objects.filter(user=request.user, challenge=pk)

        if not participation.exists():
            participation = Participation()
            participation.user = request.user
            participation.challenge_id = pk
            participation.life_left = Challenge.objects.get(pk=pk).life
            participation.save()

            return Response(ParticipationSerializer(participation).data, status=status.HTTP_201_CREATED)

        else:

            return Response(status=status.HTTP_201_CREATED)


class VerificationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            verification = Verification.objects.get(pk=pk)
            print(verification.participation_id)
            participation = Participation.objects.get(pk=verification.participation_id_id, user=request.user)
            if participation is not None:
                serializer = VerificationSerializer(verification)
                return Response(serializer.data)
            return Response(status=status.HTTP_403_FORBIDDEN)

        except:
            return Response(status=status.HTTP_403_FORBIDDEN)


class VerificationListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, challenge_id):

        try:
            participation = Participation.objects.get(challenge=challenge_id, user=request.user)
            if participation is not None:
                verifications = Verification.objects.filter(participation_id__challenge=challenge_id).order_by("-created_at")
                serializer = VerificationListSerializer(verifications, many=True)
                return Response(serializer.data)

        except:
            return Response(status=status.HTTP_403_FORBIDDEN)


class VerificationCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, challenge_id):

        try:
            participation = Participation.objects.get(challenge=challenge_id, user=request.user)
            if participation is not None:

                serializer = VerificationSerializer(data=request.data)

                if serializer.is_valid():

                    serializer.save(participation_id=participation)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(status=status.HTTP_403_FORBIDDEN)


class VerificationMyView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, challenge_id):
        try:
            participation = Participation.objects.get(challenge=challenge_id, user=request.user)
            challenge = Challenge.objects.get(pk=challenge_id)

            verifications = Verification.objects.filter(participation_id=participation).order_by("-created_at")
            serializer = VerificationSerializer(verifications, many=True)

            verification_completed_count = verifications.count()
            elapsed_days = (datetime.date.today() - challenge.start_date).days + 1
            verification_failed_count = elapsed_days - verification_completed_count

            return_data = {
                "verification_complete_count": verification_completed_count,
                "verification_failed_count": verification_failed_count,
                "total_challenge_ratio": int(verification_completed_count/elapsed_days * 100),
                "verifications": serializer.data,
            }

            return Response(return_data)

        except:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ChallengeRankView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, challenge_id):
        participation = Participation.objects.filter(challenge=challenge_id, user=request.user)
        if not participation.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            participations = Participation.objects.filter(challenge=challenge_id).order_by("-life_left")
            serializer = ParticipationRankSerializer(participations, many=True)

            temp_data = serializer.data
            temp_rank = 0
            temp_life = -1
            my_data = dict()
            for i, data in enumerate(temp_data):

                if data["life_left"] is not temp_life:

                    temp_life = data["life_left"]
                    temp_rank = temp_rank + 1

                data["rank"] = temp_rank

                if data["user"] is request.user.id:
                    my_data = data


            return_data = {
                "my": my_data,
                "challenge_life": Challenge.objects.get(pk=challenge_id).life,
                "participations": temp_data

            }


            return Response(return_data)


def dowith_celery(request):
    dowith_duhee.delay('이렇게도 되고')
    dowith_duhee.apply_async(('expires 는 선택', ), expires=600)
    return None

