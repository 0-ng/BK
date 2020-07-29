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


class Doinfo(models.Model):
    businessname = models.CharField(max_length=50, verbose_name='业务')
    username = models.CharField(max_length=50, verbose_name='用户')
    createtime = models.DateTimeField(verbose_name='创建时间')
    starttime = models.DateTimeField(verbose_name='开始执行时间')
    endtime = models.DateTimeField(verbose_name='执行结束时间', null=True, blank=True)
    iplist = models.CharField(max_length=200, verbose_name='执行列表')
    details = models.CharField(max_length=200, verbose_name='详细', null=True, blank=True)
    jobid = models.IntegerField(verbose_name='jobid')
    status_choice = [(1, '未执行'), (2, '正在执行'), (3, '执行成功'), (4, '执行失败')]
    status = models.IntegerField(choices=status_choice, verbose_name='执行状态', default=2)
    log = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["-id"]

    def to_dict(self, biz_map=None):
        if biz_map is None:
            biz_map = {}
        return {
            'id': self.id,
            'username': self.username,
            'starttime': self.starttime.strftime("%Y-%m-%d %H:%M:%S"),
            'businessname': biz_map.get(self.businessname, self.businessname),
            'iplist': self.iplist,
            'jobid': self.jobid,
            'status': '执行失败' if self.status == '3' else '执行成功',
            'details': self.details,
            'endtime': self.endtime.strftime("%Y-%m-%d %H:%M:%S") if self.endtime else "",
            'log': self.log,
        }