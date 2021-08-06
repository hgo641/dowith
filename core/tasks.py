from celery import shared_task
from dowith.celery import app


@shared_task
def dowith_duhee(data):
    print("두윗두희",data)
