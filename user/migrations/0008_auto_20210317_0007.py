# Generated by Django 2.2.17 on 2021-03-16 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20210317_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='vip_expire',
            field=models.DateTimeField(default='3000-01-01', verbose_name='VIP过期时间'),
        ),
    ]
