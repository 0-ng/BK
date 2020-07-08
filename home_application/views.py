# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from .models import SelectScript, User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from blueking.component.shortcuts import get_client_by_request

# python manage.py runserver appdev.paas-class.bktencent.com:443

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页
    """
    return render(request, 'home_application/index_home.html')


def dev_guide(request):
    """
    开发指引
    """
    return render(request, 'home_application/dev_guide.html')


def contact(request):
    """
    联系页
    """
    return render(request, 'home_application/contact.html')



def tasks(request):
    scripts = SelectScript.objects.all()
    client = get_client_by_request(request)
    result = client.cc.search_business(client)
    hostresult = client.cc.search_host(client)
    if result['message'] == 'success':
        job_names = []
        for num in range(len(result['data']['info'])):
            job_names.append(result['data']['info'][num]['bk_biz_name'])

        host_datas = []
        for num in range(len(hostresult['data']['info'])):
            host_datas.append({
                'hostid': num + 1,
                'hostip': hostresult['data']['info'][num]['host']['bk_host_innerip'],
                'hostos': hostresult['data']['info'][num]['host']['bk_os_name'],
            })
        print(host_datas)
        page = request.GET.get("page", 1)
        paginator = Paginator(host_datas, 5)
        host_datas = paginator.get_page(page)


        return render(request, 'home_application/tasks.html', {"scripts": scripts, "job_names": job_names, "host_datas": host_datas,
                                                               "page_range": paginator.page_range, "page": int(page)})
    else:
        data = {"tasks": scripts}
        return render(request, 'home_application/tasks.html', data)


def record(request):
    return render(request, 'home_application/record.html')



def update_admin(request):
    try:
        username = '1427508598'
        User.objects.create(
            username=username,
            is_staff=1,
            is_active=1,
            is_superuser=1
        )
        user = User.objects.filter(username=username).first()

        return JsonResponse({
            'username': user.username,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })
    except:
        return JsonResponse({
            'sb': 'abc',
        })



def a(request):
    return JsonResponse({
        'sb': 'abc',
    })



