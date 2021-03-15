from common.times import QN_TOKEN_EXPIRED
import time
from libs.config import QN_BUCKET, QN_CALLBACK, WEB_SERVER_HOST, QN_FILESIZE, QN_AK, QN_SK, QN_BASE_URL
from qiniu import Auth


def get_img_url(filename):
    return f'{QN_BASE_URL}/{filename}'


def make_token(uid, filename, timeout=QN_TOKEN_EXPIRED):
    ''' generate a token for qncloud server checking lisence '''
    qn_auth = Auth(QN_AK, QN_SK)
    policy = {
        'scope': QN_BUCKET,
        'deadline': int(time.time() + timeout),
        'callbackUrl': QN_CALLBACK,
        'callbackHost': WEB_SERVER_HOST,
        'callbackBody': f'uid={uid}&key=$(key)',
        'forceSaveKey': True,
        'saveKey': filename,
        'fsizeLimit': QN_FILESIZE,
        'mimeLimit': 'image/*',
    }
    token = qn_auth.upload_token(QN_BUCKET, filename, timeout, policy)
    return token
