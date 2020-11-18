from django.db import models

# Create your models here.
class AlarmDeviceTypeIdInstruntionDelay(models.Model):

    uuid = models.CharField(max_length=228, verbose_name="告警uuid")
    cloudName = models.CharField(max_length=228, verbose_name="云名称")
    tenantId = models.CharField(max_length=228, verbose_name="租户Id")
    deviceTypeId = models.CharField(max_length=228, verbose_name="模型Id") 
    ruleInterval = models.IntegerField(default=10, verbose_name="样本数据时间周期(分钟)")
    ruleDevicesDelayRatio = models.IntegerField(default=0, verbose_name="模型延迟使用率")
    ruleCmdDelayRatio = models.IntegerField(default=0, verbose_name="设备延迟使用率")
    existCmdDeviceId = models.BooleanField(default=False, verbose_name="是否存在样本周期内指令设备")
    runCmdDeviceCount = models.IntegerField(default=0, verbose_name="发送指令设备数量")
    timeoutCmdDeviceCount = models.IntegerField(default=0, verbose_name="发送指令超时设备数量")
    isAlarm = models.BooleanField(default=False, verbose_name="是否告警")
    alarmLevel = models.IntegerField(default=4, verbose_name="告警等级")
    alarmInfo = models.TextField(blank="", null="", default="", verbose_name="告警信息")
    createTime = models.DateTimeField(verbose_name="创建记录时间")
    updateTime = models.DateTimeField(verbose_name="更新记录时间")

    class Meta:
      managed = True
      db_table = 'monit_alarm_model_cmd_delay'

    def __str__(self):
        return self.alarmInfo


class DevicesInstrutionDelay(models.Model): 

    alarmId = models.ForeignKey(AlarmDeviceTypeIdInstruntionDelay, 
                               related_name="devices",
                               related_query_name="device",
                               on_delete=models.CASCADE, blank="")
    cloudName = models.CharField(max_length=228, verbose_name="云名称")
    tenantId = models.CharField(max_length=228, verbose_name="租户Id")
    deviceTypeId = models.CharField(max_length=228, verbose_name="模型Id")
    deviceId = models.CharField(max_length=228, verbose_name="设备Id")
    cmdRunCount = models.IntegerField(default=0, verbose_name="设备下发指令次数")
    cmdTimeoutCount = models.IntegerField(default=0, verbose_name="设备下发指令延迟次数")
    deviceRequestMsgIds = models.JSONField(blank="", default="", verbose_name="设备延迟指令Id")
    beginTime = models.BigIntegerField(default=0, verbose_name="开始检测模型时间")
    endTime = models.BigIntegerField(default=0, verbose_name="结束检测模型时间")
    createTime = models.DateTimeField(verbose_name="创建记录时间")

    class Meta:
      managed = True
      db_table = 'monit_device_cmd_delay'

    def __str__(self):
        return self.deviceId

    def uuid(self):
        return '%s' % self.alarmId.uuid

    def alarmInfo(self):
        return '%s' % self.alarmId.alarmInfo


