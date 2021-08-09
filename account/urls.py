from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('user/<int:pk>', views.UserView.as_view(), name="user_detail"),
    path('login', views.SocialLogin.as_view()),
    path('refresh', views.Refresh.as_view()),
    path('logout', views.LogOut.as_view())
]
