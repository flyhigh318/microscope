from django.shortcuts import render

from django.http import HttpResponse
from workcondition import metrics
from workcondition.workcondition import WorkCondition

def index(request):
    """
    index视图
    :param request: 包含了请求信息的请求对象
    :return: 响应对象
    """
    return HttpResponse("hello world!")

def get_redis_alarmId(request):
    b = metrics.get_redis_alarmId()
    return HttpResponse(b, content_type='text/plain', charset='utf-8')

def run(request):
    wk = WorkCondition()
    wk.run()
    return HttpResponse("本次工况落库采集完成!")