# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class MonitEvent(models.Model):
    uuid = models.CharField(max_length=64, blank=True, null=True)
    cloudeid = models.CharField(db_column='cloudeId', max_length=100, blank=True, null=True)  # Field name made lowercase.
    tenantid = models.CharField(db_column='tenantId', max_length=100, blank=True, null=True)  # Field name made lowercase.
    modelid = models.CharField(db_column='modelId', max_length=100, blank=True, null=True)  # Field name made lowercase.
    deviceid = models.CharField(db_column='deviceId', max_length=100, blank=True, null=True)  # Field name made lowercase.
    level = models.CharField(max_length=1)
    type = models.CharField(max_length=20)
    content = models.TextField()
    rule = models.TextField()
    createtime = models.DateTimeField(db_column='createTime')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'monit_event'


class MonitWorkcondition(models.Model):
    cloudeid = models.CharField(db_column='cloudeId', max_length=100, blank=True, null=True)  # Field name made lowercase.
    tenantid = models.CharField(db_column='tenantId', max_length=100, blank=True, null=True)  # Field name made lowercase.
    begintime = models.DateTimeField(db_column='beginTime')  # Field name made lowercase.
    endtime = models.DateTimeField(db_column='EndTime')  # Field name made lowercase.
    workingtime = models.DateTimeField(db_column='workingTime')  # Field name made lowercase.
    totalnum = models.IntegerField(db_column='totalNum')  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='createTime')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'monit_workcondition'
