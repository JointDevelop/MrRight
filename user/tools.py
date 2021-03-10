import random
from django.core.cache import cache

from common import keys
from common import times
from libs.cache import rds
from libs.sms import send_sms
from asyntasks import celery_app


def create_vcode(length=6):
    '''create validation code'''
    codeRange = '123456890'
    chars = random.sample(codeRange, length)
    vcode = ''.join(chars)
    return vcode


@celery_app.task
# @retry(XXX)  # when send_vcode is failed, we will retry it severial times
def send_vcode(phone):
    '''
    call send_sms to send message to phone with vcode.
    tips: 1、phone will be cached in memory and set expired time 10 minutes. when we call this function,
             we will try to search cache for this phonenum firstly. if we find it, meaning vcode is not
             expired, so we will not send vcode message again, othervise, vcode is expired, we need to
             send vcode message and rechache phonenum for 10 minutes.
          2、this function cache data unless program call message-agent-platform's sending message API
             successfully.
          3、when platform sending message API return successfully, API will return successful mark 
            immediatly and send_sms(.) will cache infomation，at the same time communication company will
            send the message. By the way, user maybe spend a while to receive it, but the cache is already
            countting.
    '''
    key = keys.VCODE_KEY % phone
    vcode = rds.get(key)
    if vcode:
        return True
    else:
        vcode = create_vcode()
        result = send_sms(phone, vcode)
        if result:
            rds.set(key, vcode, times.VCODE_EXPIRED)
        else:
            print('platform message send API failed...')
        return result


def gen_random_nickname(length=8):
    '''generate an random nickname'''
    nameRange = '1234567890'
    nickname = ''.join(random.choices(nameRange, k=length))
    return nickname
