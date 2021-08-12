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

@shared_task
def distribute_charge():
    yesterday = datetime.date.today() - datetime.timedelta(1)
    finished_challenges = Challenge.objects.filter(end_date = yesterday)
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
            .annotate(count = Count('participation_id')).filter(count=date_period)
        
        if completed_participants.count() == 0:
            for participation in finished_participation:#100% 완주자 없으면 전부 fee돌려주기
                participation.user.point += fc.fee
                participation.total_distribute_charge = fc.fee
                participation.save()
                participation.user.save()
        else:
            for p in all_participants:#if count==3 : point+ , else -fee
                participation = Participation.objects.get(id=p['participation_id'])
                if p['count'] == date_period: 
                    total_distribute_charge = (math.ceil(total_accumulated_fine/completed_participants.count()))+fc.fee
                else:
                    total_distribute_charge = fc.fee-(date_period-p['count'])*fine
                participation.user.point += total_distribute_charge
                participation.total_distribute_charge = total_distribute_charge
                participation.save()
                participation.user.save()