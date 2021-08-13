import datetime
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import *
from .tasks import distribute_charge, dowith_duhee
from django.db.models import Count
from rest_framework.parsers import MultiPartParser, FormParser


class ChallengeMainView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

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

    def post(self, request, *args, **kwargs):

        serializer = ChallengeSerializer(data=request.data)

        if serializer.is_valid():

            pk = serializer.save(captain=request.user)

            participation = Participation()
            participation.user = request.user
            participation.challenge_id = pk.id
            participation.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChallengeTodayView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        ongoing_challenge = Challenge.objects.filter(participation__user=request.user,
                                                     participation__verification=None,
                                                     start_date__lte=datetime.date.today(),
                                                     end_date__gte=datetime.date.today()
                                                     )
        finished_challenge = Challenge.objects.filter(participation__user=request.user,
                                                      participation__verification__isnull=False,
                                                      start_date__lte=datetime.date.today(),
                                                      end_date__gte=datetime.date.today()
                                                      )

        ongoing_serializer = ChallengeSerializer(ongoing_challenge, many=True)
        finished_serializer = ChallengeSerializer(finished_challenge, many=True)

        total_challenge = ongoing_challenge.count() + finished_challenge.count()
        complete_percentage = 0
        if total_challenge != 0:
            complete_percentage = int(finished_challenge.count() / total_challenge) * 100


        return_data = {
            "complete_percentage": complete_percentage,
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

        temp_finished_return = finished_serializer.data

        for item in temp_finished_return:
            item["total_distribute_charge"] = Participation.objects.get(challenge=item["id"], user=request.user).total_distribute_charge

        gathering_challenge = participated_challenge.filter(start_date__gt=datetime.date.today())
        gathering_serializer = GatheringChallengeSerializer(gathering_challenge, many=True)

        return_data = {

            "gathering_ongoing_count": gathering_challenge.count() + participated_ongoing_challenge.count(),
            "finished_count": finished_challenge.count(),
            "gathering": gathering_serializer.data,
            "ongoing": participated_ongoing_serializer.data,
            "finished": temp_finished_return
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
            participation.save()

            user = User.objects.get(pk=request.user.id)

            if user.point < participation.challenge.fee:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                user.point = user.point - participation.challenge.fee
                user.save()

            return Response(ParticipationSerializer(participation).data, status=status.HTTP_201_CREATED)

        else:

            return Response(status=status.HTTP_201_CREATED)


class VerificationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            verification = Verification.objects.get(pk=pk)
            participation = Participation.objects.get(pk=verification.participation_id_id, user=request.user)

            if participation is not None:
                serializer = VerificationSerializer(verification)
                print(serializer.data)
                return Response(serializer.data)
            return Response(status=status.HTTP_403_FORBIDDEN)

        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, pk):

        verifications = Verification.objects.filter(pk=pk)

        if verifications.exists():
            verification = verifications.first()
            challenges = Challenge.objects.filter(pk=verification.participation_id.challenge_id)
            if challenges.exists():
                if challenges.first().captain.id is request.user.id:
                    verification.is_verificated = True
                    verification.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, challenge_id, *args, **kwargs):

        participations = Participation.objects.filter(challenge=challenge_id, user=request.user)

        if participations.exists():

            verifications = Verification.objects.filter(participation_id=participations.first(),
                                                        created_at__year=datetime.date.today().year,
                                                        created_at__month=datetime.date.today().month,
                                                        created_at__day=datetime.date.today().day
                                                        )

            if not verifications.exists():
                try:
                    verification = Verification()
                    verification.participation_id = participations.first()
                    verification.article = request.POST["article"]
                    verification.image_url = request.FILES.get("image_url")
                    verification.save()

                    return Response(status=status.HTTP_201_CREATED)

                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "잘못된 데이터입니다."})



            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "이미 인증되었습니다."})

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "참여하지 않는 챌린지 입니다."})


class VerificationMyView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, challenge_id):
        try:
            participation = Participation.objects.get(challenge=challenge_id, user=request.user)
            challenge = Challenge.objects.get(pk=challenge_id)

            verifications = Verification.objects.filter(participation_id=participation)\
                .order_by("-created_at")
            serializer = VerificationSerializer(verifications, many=True)

            verification_completed_count = verifications.filter(is_verificated=True).count()
            elapsed_days = (datetime.date.today() - challenge.start_date).days + 1
            verification_failed_count = elapsed_days - verification_completed_count

            today_verifications = Verification.objects.filter(participation_id=participation,
                                                              created_at__year=datetime.datetime.today().year,
                                                              created_at__month=datetime.datetime.today().month,
                                                              created_at__day=datetime.datetime.today().day
                                                              )

            is_verificated = False
            if today_verifications.exists():
                is_verificated = True

            return_data = {
                "is_today_verificated": is_verificated,
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

        participations = Participation.objects.filter(challenge=challenge_id, user=request.user)
        challenge = Challenge.objects.get(pk=challenge_id)

        if not participations.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:

            verifications = Verification.objects.filter(participation_id__challenge_id=challenge_id, is_verificated=True)\
                .values('participation_id__user')\
                .annotate(verification_count=Count("participation_id__user"))\
                .order_by('-verification_count')

            return_dict = dict()
            temp_list = list()
            temp_rank = 0
            temp_count = -1

            if challenge.start_date <= datetime.date.today():
                return_dict["elapse_days"] = (datetime.date.today() - challenge.start_date).days + 1
            else:
                return_dict["elapse_days"] = 0

            for verification in verifications:
                temp_dict = dict()
                temp_dict['user_id'] = verification["participation_id__user"]
                temp_dict['verification_count'] = verification["verification_count"]

                user = User.objects.get(pk=temp_dict['user_id'])

                temp_dict["nickname"] = user.nickname

                if user.image_url:
                    temp_dict["image_url"] = user.image_url.url
                else:
                    temp_dict["image_url"] = None

                if temp_dict["verification_count"] is not temp_count:
                    temp_count = temp_dict["verification_count"]
                    temp_rank = temp_rank + 1

                temp_dict["rank"] = temp_rank

                temp_list.append(temp_dict)

                if user.id is request.user.id:
                    return_dict["my"] = temp_dict

            return_dict["participations"] = temp_list

            return Response(return_dict)


def dowith_celery(request):
    dowith_duhee.delay('이렇게도 되고')
    dowith_duhee.apply_async(('expires 는 선택', ), expires=600)
    distribute_charge.delay()
    return None

