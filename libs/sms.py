from hashlib import md5
from json import dumps
import requests
import time


API = 'https://api.mysubmail.com/message/xsend.json'
APPKEY = 'ea483dd6d5a4e2ca1329e4332897e863'

APPID = '57118'
PROJECT = 'OYL9W3'
SIGN_TYPE = 'md5'


def make_signature(args):
    '''make signature string'''
    key_val_strLst = []
    for key in sorted(args.keys()):
        key_val_strLst.append(f'{key}={args[key]}')
    key_val_str = '&'.join(key_val_strLst)
    sign_str = f'{APPID}{APPKEY}{key_val_str}{APPID}{APPKEY}'.encode('utf8')
    sign_str = md5(sign_str).hexdigest()
    return sign_str


def send_sms(phone, vcode) -> object:
    '''send phone message to user by calliing platform'''
    args = {
        'appid': APPID,
        'project': PROJECT,
        'sign_type': SIGN_TYPE,
        'to': phone,
        'timestamp': int(time.time()),
        'vars': dumps({'vcode': vcode})
    }
    args['signature'] = make_signature(args)
    response = requests.post(API, data=args)
    if response.status_code:
        result = response.json()
        if result['status'] == 'success':
            return True
        else:
            print(result['msg'])
    return False
