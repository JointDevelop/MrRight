from django.http import JsonResponse
from django.shortcuts import render
from common import keys
from common.stat_code import OK, VCODE_SEND_ERROR, VCODE_ERROR, USER_FORM_ERROR
from libs.cache import rds
from user.models import User
from user.models import Profile
from user.tools import send_vcode, gen_random_nickname
from django.core.cache import cache
from user.forms import UserForm
from user.forms import ProfileForm
from libs.http import render_json



def fetch_vcode(request):
    '''response to user by sending validated code to user by phone'''
    phonenum = request.GET.get('phonenum')
    is_successful = send_vcode(phonenum)
    if is_successful:
        # return JsonResponse({'code': 0, 'data': None})
        return render_json(code=OK, data=None)
    else:
        # return JsonResponse({'code': 1000, 'data': None})
        return render_json(code=VCODE_SEND_ERROR, data=None)


def submit_vcode(request):
    phonenum = request.POST.get('phonenum')
    vcode = request.POST.get('vcode')
    key = keys.VCODE_KEY % phonenum
    cached_Vcode = rds.get(key).decode('utf8')
    print(phonenum, vcode, key, cached_Vcode)
    if cached_Vcode and vcode == cached_Vcode:
        try:
            user = User.objects.get(phonenum=phonenum)
        except User.DoesNotExist:
            user = User.objects.create(
                phonenum=phonenum,
                nickname=gen_random_nickname()
            )
        request.session['uid'] = user.id
        # return JsonResponse({'code': 0, 'data': user.to_dict()})
        return render_json(code=OK, data=user.to_dict())
    else:
        print('vcode is expired...')
        # return JsonResponse({'code': 1001, 'data': None})
        return render_json(code=VCODE_ERROR, data=None)


def show_profile(request):
    # uid = request.session['uid']
    uid = request.uid
    user = User.objects.get(pk=uid)
    # return JsonResponse({'code': 0, 'data': user.profile.to_dict()})
    return render_json(code=OK, data=user.profile.to_dict())


def update_profile(request):
    user_form = UserForm(request.POST)
    profile_form = ProfileForm(request.POST)
    if user_form.is_valid() and profile_form.is_valid():
        # uid = request.session['uid']
        uid = request.uid
        User.objects.updata_or_create(id=uid, defaults=user_form.cleaned_data)
        Profile.objects.updata_or_create(id=uid, defaults=profile_form.cleaned_data)
        # return JsonResponse({'code': 0, 'data': None})
        return render_json(code=OK, data=None)
    else:
        err = {}
        err.update(user_form.errors)
        err.update(profile_form.errors)
        # return JsonResponse({'code': 1003, 'data': err})
        return render_json(code=USER_FORM_ERROR, data=err)


def get_qn_token(request):
    return render_json()


def qn_callback(request):
    return render_json()
