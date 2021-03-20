'''http state code'''

OK = 0  # 正常
VCODE_SEND_ERROR = 1000  # 验证码发送失败
VCODE_ERROR = 1001  # 验证码错误
LOGIN_REQUIRED = 1002  # 需要用户登陆
USER_FORM_ERROR = 1003  # 用户资料表单数据错误
SID_ERROR = 1004  # SID 错误
STYPE_ERR = 1005  # 滑动类型错误
REPEAT_SWIPE = 1006  # 重复滑动
REWIND_LIMIT = 1007  # 反悔次数达到限制
REWIND_TIMEOUT = 1008  # 反悔超时
NO_SWIPE_RECORD = 1009  # 当前还没有滑动记录
HAVE_NOT_PERM = 1010  # 用户不具有某权限



class LogicErr(Exception):
    ''' basic class for Exception class of state code '''
    code = 0
    data = None

    def __init__(self,data=None):
        self.data = data or self.__class__.__name__


def gen_logic_err(name, code):
    ''' create Exception class for every according state code '''
    attr_dict = {'code': code}
    return type(name, (LogicErr,), attr_dict)


VcodeSendErr = gen_logic_err('VcodeSendErr',code=1000)
VcodeErr = gen_logic_err('VcodeErr',code=1001)
LoginRequired = gen_logic_err('LoginRequired',code=1002)
UserFormErr = gen_logic_err('UserFormErr',code=1003)
SidErr = gen_logic_err('SidErr',code=1004)
StypeErr = gen_logic_err('StypeErr',code=1005)
RepeatSwipe = gen_logic_err('RepeatSwipe',code=1006)
RewindLimit = gen_logic_err('RewindLimit',code=1007)
RewindTimeout = gen_logic_err('RewindTimeout',code=1008)
NoSwipeRecord = gen_logic_err('NoSwipeRecord',code=1009)
HaveNotPerm = gen_logic_err('HaveNotPerm',code=1010)
