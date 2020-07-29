# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.http import JsonResponse

from . import views

urlpatterns = (
    # url(r'^$', views.a),
    # url(r'^$', views.index),
    # url(r'^dev-guide/$', views.dev_guide),
    url(r'^$', views.home),
    # url(r'^$', views.tasks),
    url(r'api/get_set/', views.get_set),
    url(r'api/execute/', views.execute_script),
    url(r'record$', views.record),
    url(r'user/update_admin$', views.update_admin),
    url(r'api/get_host/$', views.get_host),
    url(r'api/execute/$', views.execute_script),
)
