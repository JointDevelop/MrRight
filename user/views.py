from django.http import JsonResponse
from django.shortcuts import render
from common import keys
from libs.cache import rds
from user.models import User
from user.tools import send_vcode, gen_random_nickname
from django.core.cache import cache



def fetch_vcode(request):
    '''response to user by sending validated code to user by phone'''
    phonenum = request.GET.get('phonenum')
    is_successful = send_vcode(phonenum)
    if is_successful:
        return JsonResponse({'code': 0, 'data': None})
    else:
        return JsonResponse({'code': 1000, 'data': None})


def submit_vcode(request):
    phonenum = request.POST.get('phonenum')
    vcode = request.POST.get('vcode')
    key = keys.VCODE_KEY % phonenum
    cached_Vcode = rds.get(key).decode('utf8')
    print(phonenum, vcode, key,cached_Vcode)
    if cached_Vcode and vcode == cached_Vcode:
        try:
            user = User.objects.get(phonenum=phonenum)
        except User.DoesNotExist:
            user = User.objects.create(
                phonenum=phonenum,
                nickname=gen_random_nickname()
            )
        request.session['uid'] = user.id
        return JsonResponse({'code': 0, 'data': user.to_dict()})
    else:
        print('vcode is expired...')
        return JsonResponse({'code': 1001, 'data': None})


def show_profile(request):
    return JsonResponse({})


def update_profile(request):
    return JsonResponse({})


def get_qn_token(request):
    return JsonResponse({})


def qn_callback(request):
    return JsonResponse({})
