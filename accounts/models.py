from django.db import models

# Create your models here.
from django.contrib.auth.models import User
class Profile(models.Model):
    users = models.OneToOneField(User, verbose_name="用户表扩张")
    weixin = models.CharField("微信号", max_length=20)
    phone = models.CharField("手机号码", max_length=20)
