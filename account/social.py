from .models import User
import requests
import os
from rest_framework import status
from rest_framework.response import Response
from core.models import Challenge, Participation


def kakao_get_access_token(data):
    app_rest_api_key = "2589e2db71042b3e03d86f96e07aec79"
    redirect_uri = "https://dowith.likelion.app/account/kakao"
    code = data.get("code")
    url = 'https://kauth.kakao.com/oauth/token'

    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=utf-8'}

    body = {'grant_type': 'authorization_code',
            'client_id': app_rest_api_key,
            'redirect_uri': redirect_uri,
            'code': code}

    kakao_token_response = requests.post(url, headers=headers, data=body)
    kakao_token_response = kakao_token_response.json()
    error = kakao_token_response.get("error", None)
    if error:
        return None

    access_token = kakao_token_response.get("access_token")
    return access_token


def kakao_get_user(data):
    access_token = kakao_get_access_token(data)
    if not access_token:
        return None
    url = 'https://kapi.kakao.com/v2/user/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    kakao_response = requests.post(url, headers=headers)
    kakao_response = kakao_response.json()

    user, created = User.objects.get_or_create(
        provider='kakao', uid=kakao_response['id'])
    if created:
        user.nickname = kakao_response['properties'].get('nickname')
        gender = kakao_response['kakao_account'].get('gender')
        if gender == 'male':
            user.gender = 'M'
        elif gender == 'female':
            user.gender = 'F'
        user.email = kakao_response['kakao_account'].get('email')

        participation = Participation()
        participation.user = user
        participation.challenge_id = Challenge.objects.order_by('id').first()
        participation.save()


        user.save()
    return user


def naver_get_access_token(data):
    code = data.get('code')
    state = data.get('state')
    client_id = 'c1lPALZXUPhzSYaC20u8'
    client_secret = 'YDvh2NopFW'
    redirect_uri = 'http://localhost:8000/'

    response = requests.get(
        f'https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&code={code}&state={state}')
    response = response.json()
    print(response)
    error = response.get('error')
    if error:
        return None
    access_token = response.get('access_token')
    return access_token


def naver_get_user(data):
    access_token = naver_get_access_token(data)
    if not access_token:
        return None
    header = "Bearer " + access_token
    print("access token: ", access_token)

    url = 'https://openapi.naver.com/v1/nid/me'
    headers = {
        'Authorization': header
    }
    naver_response = requests.get(url, headers=headers)
    response = naver_response.json()

    user, created = User.objects.get_or_create(
        provider='naver', uid=response['response']['id'])
    if created:
        user.nickname = response['response'].get('nickname')
        gender = response['response'].get('gender')
        if gender == 'M':
            user.gender = 'M'
        elif gender == 'F':
            user.gender = 'F'
        user.email = response['response'].get('email')
        user.save()
    return user


def google_get_user(data):
    response = requests.get(
        f"https://oauth2.googleapis.com/tokeninfo?id_token={data['id_token']}")
    response = response.json()
    error = response.get('error')
    if error:
        return None

    user, created = User.objects.get_or_create(
        provider='google', uid=response['sub'])
    if created:
        user.nickname = response.get('name')
        user.email = response.get('email')
        user.save()
    return user
