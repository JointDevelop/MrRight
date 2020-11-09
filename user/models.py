from django.db import models

# Create your models here.
class User(models.Model):
    GENDER = (
        ('male','男性'),
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

    phonenum = models.CharField(max_length=16,unique=True,null=False,blank=False,verbose_name='手机')
    nickname = models.CharField(max_length=32,db_index=True,verbose_name='昵称')
    gender = models.CharField(max_length=8,choices=GENDER,verbose_name='性别')
    birthday = models.DateField(default='2000-01-01',verbose_name='生日')
    avatar = models.CharField(max_length=256,verbose_name='头像网址')
    location = models.CharField(max_length=16,choices=LOCATION,verbose_name='常居地')







