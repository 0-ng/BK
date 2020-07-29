# -*- coding: utf-8 -*-
from celery import task
from blueapps.utils.logger import logger
import datetime, time
from .models import Doinfo


@task
def async_status(client, data, biz_id, ip_id, user):
    num = 0
    tag = True
    job_id = data['job_instance_id']
    kwargs = {"bk_biz_id": biz_id,
              'job_instance_id': job_id}
    while True:
        job_data = client.job.get_job_instance_status(kwargs)
        if job_data.get('result', False):
            is_finished = job_data['data']['is_finished']
            job_instance = job_data['data']['job_instance']
            status = job_instance['status']
            create_time = job_instance['create_time'][:-6]
            start_time = job_instance['start_time'][:-6]
            if job_instance.get('end_time', ''):
                end_time = job_instance['end_time'][:-6]
            else:
                end_time = datetime.datetime.now()
            if int(status) == 2:
                time.sleep(5)
            else:
                tag = True
                break
        else:
            logger.error(u'request failed')
            num += 1
            if num > 5:
                tag = False
                break
            time.sleep(5)

    if tag:
        kwargs2 = {"bk_biz_id": biz_id,
                   'job_instance_id': job_id}
        res = client.job.get_job_instance_log(kwargs2)
        kwargs3 = {"fields": ["bk_biz_id", "bk_biz_name"], "condition": {"bk_biz_id": int(biz_id)}}
        res2 = client.cc.search_business(kwargs3)
        biz_name = res2['data']['info'][0]['bk_biz_name']

        log = []
        for info in res['data'][0]['step_results'][0]['ip_logs']:
            log.append(info['ip'] + '|' + info['log_content'])
        Doinfo.objects.create(
            businessname=biz_name,
            username=user,
            createtime=create_time,
            starttime=start_time,
            endtime=end_time,
            iplist=ip_id,
            details=is_finished,
            jobid=job_id,
            status=status,
            log=log
        )