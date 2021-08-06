from django.shortcuts import render
from .tasks import dowith_duhee
# Create your views here.

def dowith_celery(request):
    dowith_duhee.delay('이렇게도 되고')
    dowith_duhee.apply_async(('expires 는 선택', ), expires=600)
    return None