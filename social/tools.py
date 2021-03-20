from django.core.exceptions import ValidationError
from common.keys import RCMD_QUE, REWIND_KEY, RANK_KEY
from common.state_code import RewindLimit, RewindTimeout
from common.score import SWIPE_SCORE
from user.models import User
from user.models import Profile
import datetime
from social.models import Swiped
from social.models import Friend
from libs.cache import rds
from django.db.transaction import atomic
import logging

error_log = logging.getLogger('err')


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
    except ValidationError as excp:
        # TODO: print to log and throw 1006 for multiple swipe
        error_log.error(f'Swipe Error: {excp}')
        return False
    else:
        swipe.save()
        myKey = RCMD_QUE % uid
        rds.lrem(myKey, 0, sid)
        rds.zincrby(RANK_KEY, SWIPE_SCORE['like'], sid)
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
    except ValidationError as excp:
        # TODO: print to log and throw 1006 for multiple swipe
        error_log.error(f'Swipe Error: {excp}')
        return False
    else:
        swipe.save()
        myKey = RCMD_QUE % uid
        rds.lrem(myKey, 0, sid)
        rds.zincrby(RANK_KEY, SWIPE_SCORE['superlike'], sid)
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
    except ValidationError as excp:
        error_log.error(f'Swipe Error: {excp}')
        return False
    else:
        swipe.save()
        myKey = RCMD_QUE % uid
        rds.lrem(myKey, 0, sid)
        rds.zincrby(RANK_KEY, SWIPE_SCORE['dislike'], sid)


def rewind_someone(uid):
    '''
    1. rewind latest swipe that in 5 mins
    2. rewind 3 times per day
    '''
    now = datetime.datetime.now()
    rewind_key = REWIND_KEY % (uid, now.date())
    rewind_count = rds.get(rewind_key, 0)
    if rewind_count >= 3:
        raise RewindLimit
    # find latest swipe
    latest_swipe = Swiped.objects.filter(uid=uid).latest('stime')
    # check this swipe happend within 5 mins or not
    time_past = now - latest_swipe.stime
    if time_past.seconds >= 5 * 60:
        raise RewindTimeout
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


def who_like_me(uid):
    already_swiped_by_me = Swiped.objects.filter(uid=uid).values_list('sid', flat=True)
    fans_id_list = Swiped.objects \
        .filter(sid=uid, stype__in=['like', 'superlike']) \
        .exclue(uid__in=already_swiped_by_me) \
        .values_list('uid', flat=True)
    return User.objects.filter(id__in=fans_id_list)


def my_friends(uid):
    ''' get all my friends '''
    friends = User.objects.filter(id__in=Friend.friend_ids(uid))
    result = [friend.to_dict() for friend in friends]
    return result


def get_top_n_rank(top_n):
    ''' get top n on the hot rank '''
    # find top_n users
    rank_data = rds.zrevrange(RANK_KEY, 0, top_n - 1, withscores=True)
    cleaned_rank = [[int(uid), int(score)] for uid, score in rank_data]
    uids_list = [uid for uid, _ in cleaned_rank]
    users = User.objects.filter(id__in=uids_list)
    users = sorted(users, key=lambda user: uids_list.index(user.id))
    # construct detail result to return
    result = []
    exclude_fields = ['phonenum', 'birthday', 'location', 'vip_id', 'vip_expire']
    for idx, user in enumerate(users):
        info = user.to_dict(exclude=exclude_fields)
        info['rank'] = idx + 1
        info['score'] = cleaned_rank[idx][1]
        result.append(info)
    return result
