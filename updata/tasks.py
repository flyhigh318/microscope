# Create your tasks here
from logging import info
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from celery import shared_task
import json
from time import sleep
from . instrution2 import handleDeviceType 
from . instrution_test import handleDeviceTypeTest

def my_task(string):
    schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)

    PeriodicTask.objects.create(
        interval=schedule,
        name='add device %s' % string,
        task='celery_app.task.deviceTypeId_cmd_delay',
        args=json.dumps([string])
    )

@shared_task
def deviceTypeId_cmd_delay(string):
    sleep(3)
    handleDeviceType()


def my_task_1(string):
    schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)

    PeriodicTask.objects.create(
        interval=schedule,
        name='add device %s' % string,
        task='celery_app.task.test_deviceTypeId_cmd_delay',
        args=json.dumps([string])
    )

@shared_task
def test_deviceTypeId_cmd_delay(string):
    sleep(3)
    handleDeviceTypeTest()


def test1(string):
    schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)

    PeriodicTask.objects.create(
        interval=schedule,
        name='add device %s' % string,
        task='celery_app.task.hello_world',
        args=json.dumps([string])
    )

@shared_task
def hello_world(string):
    sleep(3)
    info(string)
