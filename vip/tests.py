from django.test import TestCase

# Create your tests here.
import os
import sys
import random
from datetime import date
import django


#   If you want to run independent block that imports some module of Django, you must load django enviroment
# and setup it firstly.
# 将项目文件夹的绝对路径插入到 sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
# 设置 DJANGO_SETTINGS_MODULE 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MrRight.settings')
# 初始化 Django 环境
django.setup()

from user.models import User
from vip.models import Vip, Permission, VipPermRelation


class UserTest(TestCase):

    @staticmethod
    def init_permission():
        '''创建权限模型'''
        permissions = (
            ('vipflag', '会员身份标识'),
            ('superlike', '超级喜欢'),
            ('rewind', '反悔功能'),
            ('anylocation', '任意更改定位'),
            ('unlimit_like', '无限喜欢次数'),
            ('show_fans', '查看喜欢过我的人'),
        )

        for name, desc in permissions:
            perm, _ = Permission.objects.get_or_create(name=name, description=desc)
            print('create permission %s' % perm.name)

    @staticmethod
    def init_vip():
        vip_data = (
            ('非会员', 0, 36500, 0),

            ('青铜会员(月卡)', 1, 30, 10),
            ('青铜会员(半年卡)', 1, 180, 50),
            ('青铜会员(年卡)', 1, 365, 90),

            ('白银会员(月卡)', 2, 30, 20),
            ('白银会员(半年卡)', 2, 180, 100),
            ('白银会员(年卡)', 2, 365, 180),

            ('黄金会员(月卡)', 3, 30, 40),
            ('黄金会员(半年卡)', 3, 180, 220),
            ('黄金会员(年卡)', 3, 365, 360),
        )
        for name, level, dur, price in vip_data:
            vip, _ = Vip.objects.get_or_create(
                name=name,
                level=level,
                duration=dur,
                price=price
            )
            print('create %s' % vip.name)

    @staticmethod
    def create_vip_perm_relations():
        '''创建 Vip 和 Permission 的关系'''
        # 获取权限
        vipflag = Permission.objects.get(name='vipflag')
        superlike = Permission.objects.get(name='superlike')
        rewind = Permission.objects.get(name='rewind')
        anylocation = Permission.objects.get(name='anylocation')
        unlimit_like = Permission.objects.get(name='unlimit_like')
        show_fans = Permission.objects.get(name='show_fans')

        # 给 VIP 1 分配权限
        VipPermRelation.objects.get_or_create(vip_level=1, perm_id=vipflag.id)
        VipPermRelation.objects.get_or_create(vip_level=1, perm_id=superlike.id)

        # 给 VIP 2 分配权限
        VipPermRelation.objects.get_or_create(vip_level=2, perm_id=vipflag.id)
        VipPermRelation.objects.get_or_create(vip_level=2, perm_id=superlike.id)
        VipPermRelation.objects.get_or_create(vip_level=2, perm_id=rewind.id)

        # 给 VIP 3 分配权限
        VipPermRelation.objects.get_or_create(vip_level=3, perm_id=vipflag.id)
        VipPermRelation.objects.get_or_create(vip_level=3, perm_id=superlike.id)
        VipPermRelation.objects.get_or_create(vip_level=3, perm_id=rewind.id)
        VipPermRelation.objects.get_or_create(vip_level=3, perm_id=anylocation.id)
        VipPermRelation.objects.get_or_create(vip_level=3, perm_id=unlimit_like.id)
        VipPermRelation.objects.get_or_create(vip_level=3, perm_id=show_fans.id)

    def setUp(self):
        self.init_permission()
        self.init_vip()
        self.create_vip_perm_relations()
        self.user = User.objects.create(
            phonenum='13112345678',
            nickname='HelloWorld'
        )

    def test_default_vip(self):
        self.assertEqual(self.user.vip.level,0)

    def test_set_vip(self):
        for vid_id in [2,3,4]:
            self.user.set_vip(vid_id)
            self.assertEqual(self.user.vip.level,1)

