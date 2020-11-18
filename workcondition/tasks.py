# Create your tasks here
from __future__ import absolute_import, unicode_literals
 
from logging import info
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from celery import shared_task
import json
from time import sleep
from . workcondition import WorkCondition

def workcondition_task(string):
    schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
    PeriodicTask.objects.create(
        interval=schedule,
        name='add device %s' % string,
        task='celery_app.task.postdata',
        args=json.dumps([string])
    )

@shared_task
def postdata(string):
    sleep(3)
    wk = WorkCondition()
    wk.run()
    info(string)