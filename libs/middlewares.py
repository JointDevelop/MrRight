from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class CheckLoginMiddleware(MiddlewareMixin):
    '''used to check out wether the user had login.'''

    ''' url in this list will be free to to ckeck'''
    CKECK_FREE_WHITE_LIST = [
        '/',
        'api/user/vcode/fetch',
        'api/user/vcode/submit'
    ]

    def process_request(self, request):
        '''when wsgi create request object, we run this middleware immediatly'''
        if request.path in self.CKECK_FREE_WHITE_LIST:
            return
        uid = request.session['uid']
        if isinstance(uid, int) and uid > 0:
            request.uid = uid
            return
        else:
            return JsonResponse({'code': 1002, 'data': None})
