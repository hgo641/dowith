from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('challenge', views.ChallengeMainView.as_view(), name="challenge"),
    path('challenge/today', views.ChallengeTodayView.as_view(), name="challenge_today"),
    path('challenge/my', views.ChallengeMyView.as_view(), name="challenge_my"),
    path('challenge/<int:pk>', views.ChallengeDetailView.as_view(), name="challenge_detail"),
    path('verification/my/<int:challenge_id>', views.VerificationMyView.as_view(), name="verification_my"),
    path('verification/<int:challenge_id>', views.VerificationListView.as_view(), name="verification_list"),
    path('verification/create/<int:challenge_id>', views.VerificationCreateView.as_view(), name="verification_create"),
    path('verification/<int:pk>', views.VerificationDetailView.as_view(), name="verification_detail"),
]
