# -*- coding: utf-8 -*-
import base64
import copy

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string

from .models import SelectScript, User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from blueking.component.shortcuts import get_client_by_request
from .celery_tasks import async_status

# python manage.py runserver appdev.paas-class.bktencent.com:443

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt

# 查询业务
def get_biz_info(request):
    client = get_client_by_request(request)
    kwargs = {"fields": ["bk_biz_id", "bk_biz_name"]}
    result = client.cc.search_business(kwargs)
    print("result")
    print(result)
    print("result")
    biz = []
    if result.get('result', False):
        for res in result['data']['info']:
            biz.append({
                "bk_biz_name": res['bk_biz_name'],
                "bk_biz_id": res['bk_biz_id']
            })
    # else:
    #     logger.error(u'请求业务列表失败：%s' % result.get('message'))
    return biz


# 根据业务ID查询集群
def get_set_info(request, bk_biz_id):
    client = get_client_by_request(request)
    kwargs = {"bk_biz_id": bk_biz_id}
    result = client.cc.search_set(kwargs)
    set = []
    if result.get('result', False):
        for res in result['data']['info']:
            set.append({
                "bk_set_id": res['bk_set_id'],
                "bk_set_name": res['bk_set_name'],
            })
    # else:
    #     logger.error(u'请求业务集群列表失败：%s' % result.get('message'))
    return set

# 刷新集群信息
def get_set(request):
    bk_biz_id = request.GET.get('bk_biz_id')
    if bk_biz_id:
        bk_biz_id = int(bk_biz_id)
    else:
        return JsonResponse({'result': False, 'message': "must provide biz_id to get set"})
    data = get_set_info(request, bk_biz_id)
    select_data = render_to_string('home_application/home_tbody.html', {'data': data})
    return JsonResponse({"result": True, "message": "success", "data": select_data})


# 刷新主机信息
def get_host(request):
    bk_biz_id = request.GET.get('bk_biz_id')
    bk_set_id = request.GET.get('bk_set_id')
    print("biz_id", bk_biz_id)
    print("set_id", bk_set_id)
    if bk_biz_id:
        bk_biz_id = int(bk_biz_id)
    else:
        return JsonResponse({'result': False, 'message': "must provide biz_id to get hosts"})
    data = search_host(request, bk_biz_id, bk_set_id)
    table_data = render_to_string('home_application/host_tbody.html', {'data': data})
    return JsonResponse({"result": True, "message": "success", "data": table_data})


# 根据业务ID,集群ID查询主机
def search_host(request, bk_biz_id, bk_set_id):
    client = get_client_by_request(request)
    kwargs = {"bk_biz_id": bk_biz_id,
              "condition": [{"bk_obj_id": "set",
                             "fields": [],
                             "condition": [{"field": "bk_set_id",
                                            "operator": "$eq",
                                            "value": int(bk_set_id)}]
                           }]}
    result = client.cc.search_host(kwargs)
    hosts = []
    if result.get('result', False):
        for host_info in result['data']['info']:
            hosts.append({
                "count": result['data']['count'],
                "bk_host_innerip": host_info['host']['bk_host_innerip'],
                "bk_os_name": host_info['host']["bk_os_name"],
                "host_id": host_info['host']["bk_host_id"],
                "bk_host_name": host_info['host']['bk_host_name'],
                "bk_cloud_id": host_info['host']["bk_cloud_id"][0]["id"]
            })
        return hosts
    else:
        logger.error(u'查询主机列表失败：%s' % result.get('message'))
    return hosts


def home(request):
    """
    首页
    """
    data = {"biz": get_biz_info(request)}
    print(data)
    # get_set_info(request)
    # data = {"biz": get_biz_info(request), "set": get_set_info(request)}
    # print(data['set'])
    return render(request, 'home_application/tasks.html', data)


# 执行任务
def execute_script(request):
    client = get_client_by_request(request)
    biz_id = request.POST.get('bk_biz_id')
    set_id = request.POST.get('bk_set_id')
    user = request.user

    data = search_host(request, biz_id, set_id)
    script = '''#!/bin/bash
                MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
                DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
                CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)}')
                echo -e "$MEMORY|$DISK|$CPU"
             '''
    encodestr = base64.b64encode(script.encode('utf-8'))
    script_content = str(encodestr, 'utf-8')
    if data:
        ip_id = []
        ip_info = []
        ips = {"bk_cloud_id": 0, "ip": 0}
        print(data)
        for info in data:
            ip_id.append(info['bk_host_innerip'])
            ips['ip'] = info['bk_host_innerip']
            ip_info.append(copy.deepcopy(ips))
        kwargs = {"bk_biz_id": int(biz_id),
                  "script_content": script_content,
                  "account": "root",
                  "script_type": 1,
                  "ip_list": ip_info}
        execute_data = client.job.fast_execute_script(kwargs)
        print(execute_data)
        print(execute_data.get('result'))
        if execute_data.get('result', False):
            data = execute_data['data']
            result = True
            message = str(execute_data.get('message'))
            async_status.apply_async(args=[client, data, biz_id, ip_id, user], kwargs={})
        else:
            data = []
            result = False
            message = "False"
            logger.error(u'查询主机列表失败：%s' % execute_data.get('message'))
        return JsonResponse({"result": result, "message": message, "data": data})
    else:
        return JsonResponse({'result': False, 'message': "There must be a host under the cluster", 'data': []})


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

