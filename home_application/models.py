# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#
# class WeChatUser(models.Model):
#     user = models.OneToOneField(User, models.CASCADE)
#     motto = models.CharField(max_length=100, null=True, blank=True, default="")
#     pic = models.CharField(max_length=50, null=True, blank=True, default="")
#     region = models.CharField(max_length=60, null=True, blank=True, default="")
#
#     def __str__(self):
#         return self.user.username


class SelectScript(models.Model):
    scriptname = models.CharField(max_length=50, verbose_name='脚本名称')
    scriptcontent = models.TextField(verbose_name='脚本内容')

    def __str__(self):
        return self.scriptname