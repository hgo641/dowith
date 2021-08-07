from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('challenge/main', views.ChallengeMainView.as_view(), name="challenge_main"),
    path('challenge/today', views.ChallengeTodayView.as_view(), name="challenge_today"),
    path('challenge/my', views.ChallengeMyView.as_view(), name="challenge_my"),
]
