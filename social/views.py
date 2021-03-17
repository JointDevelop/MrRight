from django.shortcuts import render

# Create your views here.
from common.score import HOT_RANK_TOP
from common.state_code import OK
from libs.http import render_json
from social import tools
from vip.tools import perm_require


def rcmd(request):
    ''' recommand users to login-User '''
    target_users = tools.recommand_users(request.uid)
    result = [u.to_dict(exclude=('phonenum','vip_id','vip_expire')) for u in target_users]
    return render_json(code=OK, data=result)


def like(request):
    '''
      right swipe will add a item of swipe into mysql, and if he/she is also like/superlike you, then you are matched
    to be friends.
    '''
    sid = int(request.POST.get('sid'))
    is_matched = tools.like_someone(request.uid, sid)
    return render_json(code=OK, data={'is_matched': is_matched})


@perm_require('superlike')
def superlike(request):
    '''
    1. upper swipe will add a item of swipe into mysql, and check whether you are matched to be friends.
    2. you will be added into he/she recommand-list.
    '''
    sid = int(request.POST.get('sid'))
    is_matched = tools.superlike_someone(request.uid, sid)
    return render_json(code=OK, data={'is_matched': is_matched})


def dislike(request):
    ''' left swipe: dislike '''
    sid = int(request.POST.get('sid'))
    tools.dislike_someone(request.id, sid)
    return render_json(code=OK)


@perm_require('rewind')
def rewind(request):
    ''' 3 times per day '''
    tools.rewind_someone(request.uid)
    return render_json(code=OK)


@perm_require('show_fans')
def fans(request):
    ''' fans is the people that he/she like/superlike you, but they aren't friends of you and you aren't dislike them'''
    users = tools.who_like_me(request.uid)
    result = [user.to_dict(exclude=('phonenum','vip_id','vip_expire')) for user in users]
    return render_json(code=OK, data=result)


def friends(request):
    ''' get my friends list '''
    data = tools.my_friends(request.uid)
    return render_json(code=OK, data=data)


def rank(request):
    ''' hot rank for users 50 ahead'''
    rand_data = tools.get_top_n_rank(HOT_RANK_TOP)
    return render_json(code=OK,data=rand_data)
