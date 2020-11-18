from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^index/$', views.index),
    url(r'^run/$', views.run),
    url(r'^metric/$', views.get_redis_alarmId),
]