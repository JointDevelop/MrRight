import datetime

from django.db import models


# Create your models here.
from common.vip_info import VIP_LOWEST_LEVEL
from vip.models import Vip


class User(models.Model):
    GENDER = (
        ('male', '男性'),
        ('female', '女性'),
    )
    LOCATION = (
        ("北京", "北京"),
        ("上海", "上海"),
        ("深圳", "深圳"),
        ("郑州", "郑州"),
        ("西安", "西安"),
        ("成都", "成都"),
        ("沈阳", "沈阳"),
    )

    phonenum = models.CharField(max_length=16, unique=True, null=False, blank=False, verbose_name='手机')
    nickname = models.CharField(max_length=32, db_index=True, null=False, verbose_name='昵称')
    gender = models.CharField(max_length=8, choices=GENDER, default='male', verbose_name='性别')
    birthday = models.DateField(default='2000-01-01', verbose_name='生日')
    avatar = models.CharField(max_length=256, default='', verbose_name='头像网址')
    location = models.CharField(max_length=16, choices=LOCATION, default='北京', verbose_name='常居地')

    vip_id = models.IntegerField(default=VIP_LOWEST_LEVEL, verbose_name='用户购买的VIP的ID')
    vip_expire = models.DateTimeField(default='3000-01-01', verbose_name='VIP过期时间')

    def to_dict(self):
        return {
            'id': self.id,
            'phonenum': self.phonenum,
            'nickname': self.nickname,
            'gender': self.gender,
            'birthday': str(self.birthday),
            'avatar': self.avatar,
            'location': self.location
        }

    @property
    def profile(self):
        '''easy to get user's profile without foreign key between User and Profile'''
        if not hasattr(self, '_profile'):
            self._profile, _ = Profile.objects.get_or_create(id=self.id)
        return self._profile
2440151307LMlmLMlm
    @property
    def vip(self):
        ''' user's vip '''
        if self.is_vip_expired():
            self.set_vip(VIP_LOWEST_LEVEL)
        if not hasattr(self, '_vip'):
            self._vip = Vip.objects.get(id=self.vip_id)
        return self._vip

    def is_vip_expired(self):
        return datetime.datetime.now() >= self.vip_expire

    def set_vip(self,vip_id):
        self._vip = Vip.objects.get(id=vip_id)
        self.vip_id = vip_id
        self.vip_expire = datetime.datetime.now() + datetime.timedelta(self._vip.duration)
        self.save()


class Profile(models.Model):
    '''User's profile for profile-Page'''
    dating_location = models.CharField(max_length=16, choices=User.LOCATION, default='北京', verbose_name='目标城市')
    dating_gender = models.CharField(max_length=16, choices=User.GENDER, default='female', verbose_name='匹配的性别')
    min_distance = models.IntegerField(default=1, verbose_name='最小查找范围')
    max_distance = models.IntegerField(default=10, verbose_name='最大查找范围')
    min_dating_age = models.IntegerField(default=18, verbose_name='最小交友年龄')
    max_dating_age = models.IntegerField(default=50, verbose_name='最大交友年龄')
    vibration = models.BooleanField(default=True, verbose_name='开启震动')
    only_matched = models.BooleanField(default=True, verbose_name='不让陌生人看我的相册')
    auto_play = models.BooleanField(default=True, verbose_name='自动播放视频')

    def to_dict(self):
        return {
            'id': self.id,
            'dating_location': self.dating_location,
            'dating_gender': self.dating_gender,
            'min_distance': self.min_distance,
            'max_distance': self.max_distance,
            'min_dating_age': self.min_dating_age,
            'max_dating_age': self.max_dating_age,
            'vibration': self.vibration,
            'only_matched': self.only_matched,
            'auto_play': self.auto_play
        }
