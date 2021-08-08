import re

from django.conf import settings
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import jwt

from .jwt import generateAccessToken, generateRefreshToken
from .models import *
from .models import RefreshToken
from .serializers import *
from .social import google_get_user, kakao_get_user, naver_get_user

# Create your views here.


class SocialLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        user = None
        if data.get("provider") == 'kakao':
            user = kakao_get_user(data)
        elif data.get("provider") == 'naver':
            user = naver_get_user(data)
        elif data.get("provider") == 'google':
            user = google_get_user(data)
        if user:
            refresh_obj = RefreshToken.objects.create(user=user)
            return Response(
                status=status.HTTP_200_OK,
                data={"status": "SUCCESS", "message": "정상적으로 로그인 되었습니다.", "access": generateAccessToken(user),
                      "refresh": generateRefreshToken(user, request, refresh_obj)})
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"status": "FAILED", "message": "로그인 처리중 오류가 발생하였습니다."})


class Refresh(APIView):
    def post(self, request):
        data = request.data
        access = data.get("accessToken")
        refresh = data.get("refreshToken")
        if not access or not refresh:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"status": "FAILED", "message": "토큰값이 정상적으로 전달되지 않았습니다."},
            )
        try:
            access_data = jwt.decode(
                access,
                settings.SECRET_KEY,
                algorithms="HS256",
                audience="urn:korowd:user",
                options={"verify_exp": False},
            )
            refresh_data = jwt.decode(
                refresh, settings.SECRET_KEY, algorithms="HS256")
        except:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"status": "FAILED", "message": "유효한 인증 정보를 찾을 수 없습니다."},
            )
        refresh_obj = RefreshToken.objects.get(id=refresh_data["sub"])
        if int(refresh_obj.last_refreshed.timestamp()) != refresh_data["iat"]:
            refresh_list = refresh_obj.user.refresh_tokens.all()
            for refresh in refresh_list:
                refresh.delete()
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={
                    "status": "FAILED",
                    "message": "토큰 탈취가 의심됩니다. 계정 안전을 위해 해당 계정에 로그인 된 모든 기기가 로그아웃 처리 되었습니다.",
                },
            )
        if str(refresh_obj.user.id) != access_data["sub"]:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={
                    "status": "FAILED",
                    "message": "토큰의 정보가 일치하지 않습니다.",
                },
            )
        refresh = generateRefreshToken(refresh_obj.user, request, refresh_obj)
        access = generateAccessToken(refresh_obj.user)
        return Response(
            data={
                "status": "SUCCESS",
                "message": "Refresh Success",
                "accessToken": access,
                "refreshToken": refresh,
            }
        )


class LogOut(APIView):
    def post(self, request):
        data = request.data
        refresh = data.get("refreshToken")
        if not refresh:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"status": "FAILED", "message": "토큰값이 정상적으로 전달되지 않았습니다."},
            )
        try:
            refresh_data = jwt.decode(
                refresh, settings.SECRET_KEY, algorithms="HS256")
        except:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"status": "FAILED", "message": "인증정보가 유효하지 않거나 만료되었습니다."},
            )
        if not RefreshToken.objects.filter(id=refresh_data["sub"]).exists:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={
                    "status": "FAILED",
                    "message": "유효한 인증 정보를 찾을 수 없습니다. 이미 로그아웃 되어 있습니다.",
                },
            )
        refresh_obj = RefreshToken.objects.get(id=refresh_data["sub"])
        refresh_obj.delete()
        return Response(data={"status": "SUCCESS", "message": "로그아웃 처리 되었습니다."})


class ForceLogOut(APIView):
    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"status": "FAILED", "message": "토큰 값이 없습니다."},
            )
        if re.match("[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$", token) is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"status": "FAILED", "message": "토큰 형식이 올바르지 않습니다."},
            )
        if not RefreshToken.objects.filter(id=token).exists():
            return Response(
                data={
                    "status": "FAILED",
                    "message": "요청한 토큰을 찾을 수 없습니다. 이미 로그아웃 된 토큰일 수 있습니다.",
                }
            )
        refresh_obj = RefreshToken.objects.get(id=token)
        refresh_obj.delete()
        return Response(
            data={"status": "SUCCESS", "message": "해당 토큰이 서버에서 강제 로그아웃 처리 되었습니다."}
        )


class UserView(APIView):
    def get(self, request, pk):

        serializer = UserSerializer(request.user)
        if request.user.id is pk:
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
