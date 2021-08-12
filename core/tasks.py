from celery import shared_task
from dowith.celery import app
from .models import Challenge, Participation, Verification
from django.db.models import Q,Count
from django.contrib.auth import get_user_model
import datetime
import math

@shared_task
def dowith_duhee(data):
    print("두윗두희", data)

@shared_task
def dowith_test():
    c = Challenge.objects.all().first()
    print(c)

# @shared_task
# def distribute_reward():
#     yesterday = datetime.date.today() - datetime.timedelta(1)
#     print(yesterday)
#     print(datetime.date.today())
#     finished_challenges = Challenge.objects.filter(end_date = yesterday)
#     print(finished_challenges)
#     for fc in finished_challenges:
#         finished_participation = Participation.objects.filter(challenge = fc)
#         verification_count = Verification.objects.filter(participation_id__in = finished_participation).count()
#         date_period = (fc.end_date - fc.start_date).days+1
#         required_verification =date_period*finished_participation.count()
#         fine = math.ceil(fc.fee/date_period)

#         total_accumulated_fine = (required_verification-verification_count)*fine
        
#         finished_verifications = Verification.objects.filter(participation_id__in = finished_participation)
#         completed_participants = finished_verifications.values('participation_id')\
#             .annotate(count = Count('participation_id')).filter(count=3)#filter count=3없애고
        
#         if completed_participants == None:
#             pass
#         else:
#             for cp in completed_participants:#if count==3 : point+ , else -fee
#                 completed_user = get_user_model().objects.get(id=cp['participation_id'])
#                 completed_user.point += math.ceil(total_accumulated_fine/completed_participants.count())
#                 completed_user.save()

@shared_task
def distribute_charge():
    yesterday = datetime.date.today() - datetime.timedelta(1)
    print(yesterday)
    print(datetime.date.today())
    finished_challenges = Challenge.objects.filter(end_date = yesterday)
    print(finished_challenges)
    for fc in finished_challenges:
        finished_participation = Participation.objects.filter(challenge = fc)
        verification_count = Verification.objects.filter(participation_id__in = finished_participation).count()
        date_period = (fc.end_date - fc.start_date).days+1
        required_verification =date_period*finished_participation.count()
        fine = math.ceil(fc.fee/date_period)

        total_accumulated_fine = (required_verification-verification_count)*fine
        
        finished_verifications = Verification.objects.filter(participation_id__in = finished_participation)
        all_participants = finished_verifications.values('participation_id')\
            .annotate(count = Count('participation_id'))#.filter(count=3)#filter count=3없애고

        completed_participants = finished_verifications.values('participation_id')\
            .annotate(count = Count('participation_id')).filter(count=3)
        #total_distribute_charge
        if completed_participants == None:
            for p in all_participants:
                user = get_user_model().objects.get(id=p['participation_id'])
                user.point += fc.fee
                user.total_distribute_charge = fc.fee
                user.save()
        else:
            for p in all_participants:#if count==3 : point+ , else -fee
                user = get_user_model().objects.get(id=p['participation_id'])
                if p['count'] == date_period: 
                    total_distribute_charge = (math.ceil(total_accumulated_fine/completed_participants.count()))+fc.fee
                    print(user)
                else:
                    total_distribute_charge = fc.fee-(date_period-p['count'])*fine
                user.point += total_distribute_charge
                user.total_distribute_charge = total_distribute_charge
                user.save()