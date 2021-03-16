from django.core.exceptions import ValidationError
from common.keys import RCMD_QUE, REWIND_K
from user.models import User
from user.models import Profile
import datetime
from social.models import Swiped
from social.models import Friend
from libs.cache import rds
from django.db.transaction import atomic


def recommand_from_queue(uid):
    ''' recommand from priority queue '''
    myKey = RCMD_QUE % uid
    uids_list = [int(sid) for sid in rds.lrange(myKey, 0, 19)]
    return User.objects.filter(id__in=uids_list)


def recommand_from_db(uid, num):
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
        users_db = set(recommand_from_db(uid, remain_nums))
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
        rds.lrem(myKey, 0, sid)
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
    swipe = Swiped(uid=uid, sid=sid, stype='dislike')
    try:
        swipe.full_clean()
    except ValidationError:
        print('Error: swipe error ...')
        return False
    else:
        swipe.save()
        myKey = RCMD_QUE % uid
        rds.lrem(myKey, 0, sid)


def rewind_someone(uid):
    '''
    1. rewind latest swipe that in 5 mins
    2. rewind 3 times per day
    '''
    now = datetime.datetime.now()
    rewind_key = REWIND_K % (uid, now.date())
    rewind_count = rds.get(rewind_key, 0)
    if rewind_count >= 3:
        # TODO: return state code 1007
        pass
    # find latest swipe
    latest_swipe = Swiped.objects.filter(uid=uid).latest('stime')
    # check this swipe happend within 5 mins or not
    time_past = now - latest_swipe.stime
    if time_past.seconds >= 5 * 60:
        # TODO: return state code 1008
        pass
    # make it be a transaction
    with atomic():
        # if latest swipe cause 'you are frineds', you have to retrive this friendship
        if latest_swipe.stype in ['like', 'superlike']:
            Friend.break_off(uid, latest_swipe.sid)
        # delete latest swipe record
        latest_swipe.delete()
        # update rewind count
        rds.set(rewind_key, rewind_count + 1, 24 * 60 * 60 + 10)
    return None
