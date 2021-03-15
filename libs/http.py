import json


from django.http import HttpResponse

from MrRight import settings
from common.state_code import OK


def render_json(code=OK,data=None):
    '''make a template for json string'''
    result = {
        'code': code,
        'data': data
    }
    if settings.DEBUG:
        '''in DEBUG mod: make style of json string friendly to show'''
        json_str = json.dumps(result,ensure_ascii=False,indent=4,sort_keys=True)
    else:
        json_str = json.dumps(result,ensure_ascii=False,separators=(',',';'))
    response = HttpResponse(json_str,content_type='application/json')
    return response
