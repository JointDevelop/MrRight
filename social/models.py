from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
class Swiped(models.Model):
    ''' swipe memory '''
    STYPES = (
        ('like', '喜欢'),
        ('superlike', '超级喜欢'),
        ('dislike', '不喜欢'),
    )
    uid = models.IntegerField(verbose_name='滑动者的ID')
    sid = models.IntegerField(verbose_name='被滑动者的ID')
    stype = models.CharField(max_length=10, choices=STYPES, verbose_name='滑动类型')
    stime = models.DateField(auto_now_add=True, verbose_name='滑动时间')

    class Meta:
        unique_together = ['uid', 'sid']

    @classmethod
    def is_liked(cls,uid,sid):
        '''
        return: True -- like
                False -- dislike
                None -- no swipe record
        '''
        try:
            swipe = cls.objects.filter(uid=uid,sid=sid).exists()
        except cls.DoesNotExist:
            return None
        else:
            return False if swipe.stype == 'dislike' else True




class Friend(models.Model):
    ''' relationship of friends '''
    uid1 = models.IntegerField(verbose_name='UID1')
    uid2 = models.IntegerField(verbose_name='UID2')

    class Meta:
        unique_together = ['uid1', 'uid2']

    @classmethod
    def make_friends(cls, uid1, uid2):
        ''' make friends '''
        uid1, uid2 = sorted([uid1, uid2])
        cls.objects.create(uid1=uid1, uid2=uid2)
