from common import keys
from common.keys import PROFILE_KEY, MODEL_KEY
from common.state_code import OK, VCODE_SEND_ERROR, VCODE_ERROR, USER_FORM_ERROR, VcodeErr, UserFormErr
from libs.cache import rds
from libs.qncloud import make_token, get_img_url
from user.models import User
from user.models import Profile
from user.tools import send_vcode, gen_random_nickname
from django.core.cache import cache
from user.forms import UserForm
from user.forms import ProfileForm
from libs.http import render_json
import logging


info_log = logging.getLogger('inf')


def fetch_vcode(request):
    '''response to user by sending validated code to user by phone'''
    phonenum = request.GET.get('phonenum')
    # # Case 1: Do not use celery
    # is_successful = send_vcode(phonenum)
    # if is_successful:
    #     return render_json(code=OK, data=None)
    # else:
    #     return render_json(code=VCODE_SEND_ERROR, data=None)
    # Case 2: Use celery
    # Because of celery, we do not necessary to wait the message platform send messages sucessfully. So we do not need
    # the state code to make a response to return the visitor.
    send_vcode.delay(phonenum)
    return render_json(code=OK,data=None)


def submit_vcode(request):
    phonenum = request.POST.get('phonenum')
    vcode = request.POST.get('vcode')
    key = keys.VCODE_KEY % phonenum
    print(key)
    cached_Vcode = rds.get(key).decode('utf8')
    print(phonenum, vcode, key, cached_Vcode)
    if cached_Vcode and vcode == cached_Vcode:
        try:
            user = User.objects.get(phonenum=phonenum)
            info_log.info(f'Login: User({user.id})')
        except User.DoesNotExist:
            user = User.objects.create(
                phonenum=phonenum,
                nickname=gen_random_nickname()
            )
            info_log.info(f'Register: User({user.id})')
        request.session['uid'] = user.id
        # return JsonResponse({'code': 0, 'data': user.to_dict()})
        return render_json(code=OK, data=user.to_dict())
    else:
        # print('vcode is expired...')
        # return JsonResponse({'code': 1001, 'data': None})
        raise VcodeErr
        # return render_json(code=VCODE_ERROR, data=None)


def show_profile(request):
    # uid = request.session['uid']
    uid = request.uid
    profile_key = PROFILE_KEY % uid
    profile = rds.get(profile_key)
    info_log.debug(f'Profile Read From Cache: User({uid})')
    if profile is None:
        user = User.objects.get(pk=uid)
        profile = user.profile.to_dict()
        info_log.debug(f'Profile Read From DB: User({uid})')
        rds.set(profile_key,profile)
        info_log.debug(f'Profile Cached: User({uid})')
    # return JsonResponse({'code': 0, 'data': user.profile.to_dict()})
    return render_json(code=OK, data=profile)


def update_profile(request):
    user_form = UserForm(request.POST)
    profile_form = ProfileForm(request.POST)
    if user_form.is_valid() and profile_form.is_valid():
        # uid = request.session['uid']
        uid = request.uid
        #   use 'update_or_create' for protecting database from directly calling this updating API by warm without
        # created User or Profile. But when provided a middleware to check login state, it can be sure User has already
        # been created. So when he visit to profile page, that must call show_profile and 'user.profile' must call
        # get_or_create to create profile, he whill be update safely and not nessisary to call update_or_create!
        # We still use update_or_create, because we may close some middlewares for testing, it will cause some problems.
        User.objects.update_or_create(id=uid, defaults=user_form.cleaned_data)
        Profile.objects.update_or_create(id=uid, defaults=profile_form.cleaned_data)
        #   delete profile cached in redis. when login-user come to profile page again, it will call show_profile(.) and
        # cache new data again
        profile_key = PROFILE_KEY % uid
        model_key_User = MODEL_KEY % ('User', uid)
        model_key_Profile = MODEL_KEY % ('Profile', uid)
        rds.delete(profile_key)  # TODO: When rewrite update API of orm, it will be absorted into update API.
        rds.delete(model_key_User,model_key_Profile) # TODO: same above
        info_log.debug(f'Updating Profile Lead Cached Profile Delete: User({uid})')
        # return JsonResponse({'code': 0, 'data': None})
        return render_json(code=OK, data=None)
    else:
        err = {}
        err.update(user_form.errors)
        err.update(profile_form.errors)
        # return JsonResponse({'code': 1003, 'data': err})
        raise UserFormErr(err)
        # return render_json(code=USER_FORM_ERROR, data=err)


def get_qn_token(request):
    '''
      When visitor call for uploading pictures, server will generate a token lisence back to visitor, so that visitor
    can take it to call for clound-memory API to upload pictures.
    '''
    filename = f'Avatar-{request.uid}'
    token = make_token(request.uid, filename)
    data = {
        'key': filename,
        'token': token
    }
    return render_json(code=OK, data=data)


def qn_callback(request):
    '''
      When visitor bring a token and pictrues to call clound-memory API, clound server will ckeck the token and save the
    pictrues, and then call web server' callback-API to give the URL of pictures to web server. Web server will return
    Json infomation back to clound server, and the clound server bring it to visitor.
    '''
    uid = request.POST.get('uid')
    key = request.POST.get('key')
    avatar_url = get_img_url(key)
    User.objects.filter(uid=uid).update(avatar=avatar_url)
    rds.delete(MODEL_KEY % ('User',uid))  # TODO: When rewrite update API of orm, it will be absorted into update API.
    return render_json(code=OK, data=avatar_url)
