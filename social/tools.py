from django.core.exceptions import ValidationError
from common.keys import RCMD_QUE
from user.models import User
from user.models import Profile
import datetime
from social.models import Swiped
from social.models import Friend
from libs.cache import rds


def recommand_from_queue(uid):
    ''' recommand from priority queue '''
    myKey = RCMD_QUE % uid
    uids_list = [int(sid) for sid in rds.lrange(myKey, 0, 19)]
    return User.objects.filter(id__in=uids_list)


def recommand_from_db(uid,num):
    ''' recomand from database '''
    target_profile = Profile.objects.get(id=uid)
    # calculate birthday
    today = datetime.date.today()
    earliest_birthday = today - datetime.timedelta(target_profile.max_dating_age * 365)
    latest_birthday = today + datetime.timedelta(target_profile.min_dating_age * 365)
    # find the users who matched the basic condition.
    target_users = User.objects.filter(
        gender=target_profile.dating_gender,
        location=target_profile.dating_location,
        birthday__range=[earliest_birthday, latest_birthday]
        # TODO: others like 'min_distance' and 'max_distance' wait to be deal with. We pass them temperarily.
    )
    # Exclude the users who had already been swiped 'like'/'superlike'/'dislike' by login-User.
    already_swape_list = Swiped.objects.filter(uid=uid).values_list('sid', flat=True)
    target_users = target_users.exclude(id__in=already_swape_list)[:20]
    return target_users


def recommand_users(uid):
    ''' Algorithm of recommanding users'''
    users_que = set(recommand_from_queue(uid))
    remain_nums = 20 - len(users_que)
    if remain_nums > 0:
        users_db = set(recommand_from_db(uid,remain_nums))
        users = users_que | users_db
    return users


def like_someone(uid, sid):
    ''' right swipe someone: like '''
    # TODO: 1. add swipe action to mysql
    swipe = Swiped(uid=uid, sid=sid, stype='like')
    try:
        swipe.full_clean()
    except ValidationError:
        # TODO: print to log and throw 1006 for multiple swipe
        print('Error: error swipe ...')
        return False
    else:
        swipe.save()
        myKey = RCMD_QUE % uid
        rds.lrem(myKey,0,sid)
    # TODO: 2. check he/she like/super login-User or not, if it is true, then they are friends
    if Swiped.is_liked(sid, uid):
        Friend.make_friends(uid, sid)
        return True
    else:
        return False


def superlike_someone(uid, sid):
    ''' upper swipe someone: superlike '''
    # TODO: 1. add swipe action to mysql
    swipe = Swiped(uid=uid, sid=sid, stype='superlike')
    try:
        swipe.full_clean()
    except ValidationError:
        # TODO: print to log and throw 1006 for multiple swipe
        print('Error: error swipe ...')
        return False
    else:
        swipe.save()
        myKey = RCMD_QUE % uid
        rds.lrem(myKey, 0, sid)
    # TODO: 2.1 check he/she like/super login-User or not, if it is true, then they are friends.
    # TODO: 2.2 if he/she is not dislike you, then add he/she to his/her recommand-list.
    liked = Swiped.is_liked(sid, uid)
    if liked is True:
        Friend.make_friends(uid, sid)
        return True
    elif liked is False:
        return False
    else:
        he_or_she_recommand_key = RCMD_QUE % sid
        rds.rpush(he_or_she_recommand_key, uid)
        return False


def dislike_someone(uid, sid):
    ''' dislike comeone '''
    swipe = Swiped(uid=uid,sid=sid,stype='dislike')
    try:
        swipe.full_clean()
    except ValidationError:
        print('Error: swipe error ...')
        return False
    else:
        swipe.save()
        myKey = RCMD_QUE % uid
        rds.lrem(myKey, 0, sid)