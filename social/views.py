from django.shortcuts import render

# Create your views here.
from common.state_code import OK
from libs.http import render_json
from social import tools


def rcmd(request):
    ''' recommand users to login-User '''
    target_users = tools.recommand_users(request.uid)
    result = [u.to_dict() for u in target_users]
    return render_json(code=OK, data=result)


def like(request):
    '''
      right swipe will add a item of swipe into mysql, and if he/she is also like/superlike you, then you are matched
    to be friends.
    '''
    sid = int(request.POST.get('sid'))
    is_matched = tools.like_someone(request.uid, sid)
    return render_json(code=OK,data={'is_matched':is_matched})


def superlike(request):
    '''
    1. upper swipe will add a item of swipe into mysql, and check whether you are matched to be friends.
    2. you will be added into he/she recommand-list.
    '''
    sid = int(request.POST.get('sid'))
    is_matched = tools.superlike_someone(request.uid, sid)
    return render_json(code=OK,data={'is_matched':is_matched})


def dislike(request):
    ''' left swipe: dislike '''
    sid = int(request.POST.get('sid'))
    tools.dislike_someone(request.id,sid)
    return render_json()


def rewind(request):
    ''' 3 times per day '''
    tools.rewind_someone(request.uid)
    return render_json()


def fans(request):
    return render_json()


def friends(request):
    return render_json()


def rank(request):
    return render_json()
