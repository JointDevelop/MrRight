from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from MrRight.settings import STATIC_URL
from common.state_code import LOGIN_REQUIRED, LogicErr, LoginRequired
from libs.http import render_json
import logging

error_log = logging.getLogger('err')


class CheckLoginMiddleware(MiddlewareMixin):
    '''used to check out wether the user had login.'''

    ''' url in this list will be free to to ckeck'''
    CKECK_FREE_WHITE_LIST = [
        '/',
        '/index/',
        '/api/user/vcode/fetch',
        '/api/user/vcode/submit',
        '/qiniu/callback',
        '/api/social/rank'
    ]

    def process_request(self, request):
        '''when wsgi create request object, we run this middleware immediatly'''
        if request.path in self.CKECK_FREE_WHITE_LIST or request.path.startswith(STATIC_URL):
            return

        uid = request.session.get('uid')
        if isinstance(uid, int) and uid > 0:
            request.uid = uid
            return
        else:
            return render_json(code=LoginRequired.code)
            # return render_json(code=LOGIN_REQUIRED, data=None)


class LogicErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, excp):
        if isinstance(excp, LogicErr):
            error_log.error(f'code: {excp.code} data:{excp.data}')
            return render_json(code=excp.code, data=excp.data)
