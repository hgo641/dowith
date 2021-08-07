from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('user/<int:pk>', views.UserView.as_view(), name="user_detail"),
]
