'''http state code'''

OK = 0  # 正常
VCODE_SEND_ERROR = 1000  # 验证码发送失败
VCODE_ERROR = 1001  # 验证码错误
LOGIN_REQUIRED = 1002  # 需要用户登陆
USER_FORM_ERROR = 1003  # 用户资料表单数据错误
SID_ERROR= 1004  # SID 错误
STYPE_ERR = 1005  # 滑动类型错误
REPEAT_SWIPE = 1006  # 重复滑动
# = 1007  # 反悔次数达到限制
# = 1008  # 反悔超时
# = 1009  # 当前还没有滑动记录
# = 1010  # 用户不具有某权限

class LogicErr(Exception):
    code = 0

class RewindLimit(LogicErr):
    # 反悔次数达到限制
    code = 1007

class RewindTimeout(LogicErr):
    # 反悔超时
    code = 1008






