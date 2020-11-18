from django.shortcuts import render

from . instrution2 import handleDeviceType
# Create your views here.
from django.http import HttpResponse

from . metrics import  get_redis_alarmId
from . loginuser import createLoginUser

from django.shortcuts import redirect, reverse

def login(request):
    """
    :redirect login
    """
    return redirect("/admin")


def index(request):
    """
    index视图
    :param request: 包含了请求信息的请求对象
    :return: 响应对象
    """
    msg = createLoginUser()
    return HttpResponse("Hello,\n {}".format(msg))


def instruction(request):
    handleDeviceType()
    info = "数据处理完毕"
    return HttpResponse(info)


def metrics(request):   
    b = get_redis_alarmId()
    return HttpResponse(b,content_type="text/plain",charset='utf-8')
