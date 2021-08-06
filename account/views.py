from django.shortcuts import render, redirect, get_object_or_404
from .models import *

# Create your views here.


def tst(request):
    user = User.objects.create_user('naver', '123', 'nick')
    user.save()
    return redirect('/')