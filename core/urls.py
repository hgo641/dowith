from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('challenge', views.ChallengeMainView.as_view(), name="challenge"),
    path('challenge/today', views.ChallengeTodayView.as_view(), name="challenge_today"),
    path('challenge/my', views.ChallengeMyView.as_view(), name="challenge_my"),
    path('challenge/detail/<int:pk>', views.ChallengeDetailView.as_view(), name="challenge_detail"),
]
