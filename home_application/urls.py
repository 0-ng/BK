# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.http import JsonResponse

from . import views

urlpatterns = (
    # url(r'^$', views.a),
    # url(r'^$', views.index),
    url(r'^dev-guide/$', views.dev_guide),
    url(r'^contact/$', views.contact),
    url(r'^$', views.tasks),
    url(r'tasks$', views.tasks),
    url(r'record$', views.record),
    url(r'user/update_admin$', views.update_admin),
)
