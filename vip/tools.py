from common.state_code import HaveNotPerm
from user.models import User


def perm_require(perm_name):
    def outer(view_func):
        def inner(request,*args,**kargs):
            user = User.objects.get(id=request.uid)
            if user.vip.has_perm(perm_name):
                return view_func(request,*args,**kargs)
            else:
                raise HaveNotPerm
        return inner
    return outer
