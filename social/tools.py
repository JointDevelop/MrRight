from django.core.exceptions import ValidationError

from common.keys import RCMD_QUE
from user.models import User
from user.models import Profile
import datetime
from social.models import Swiped
from social.models import Friend
from libs.cache import rds


def recommand_users(uid):
    ''' Algorithm of recommanding users'''
    target_profile = Profile.objects.get(id=uid)
    today = datetime.date.today()
    earliest_birthday = today - datetime.timedelta(target_profile.max_dating_age * 365)
    latest_birthday = today + datetime.timedelta(target_profile.min_dating_age * 365)
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
        rds.lpush(he_or_she_recommand_key,uid)
        return False
