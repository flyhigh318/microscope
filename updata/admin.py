from django.contrib import admin
from updata.models import *
# Register your models here.
admin.site.site_header = '显微镜监控系统'   #后台显示
admin.site.site_title = '根云平台显微镜'     #网站名称
# admin.site.site_url = 'www.baidu.com'
# admin.site.register(AlarmDeviceTypeIdInstruntionDelay)

@admin.register(AlarmDeviceTypeIdInstruntionDelay)
class AlarmDeviceTypeIdInstruntionDelayAdmin(admin.ModelAdmin):
    list_display = ['uuid','tenantId','deviceTypeId','alarmInfo','updateTime']
    search_fields = ['uuid','tenantId','deviceTypeId']

# @admin.register(DevicesInstrutionDelay)
# class DevicesInstrutionDelayAdmin(admin.ModelAdmin):
#     list_display = ['deviceId', 'tenantId', 'uuid', 'alarmInfo']
#     search_fields = ['tenantId', 'alarmId__uuid', 'deviceTypeId', 'deviceId']
    