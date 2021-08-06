from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('challenge', views.ChallengeView.as_view(), name="test"),
]
