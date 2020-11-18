# -*- coding: utf-8 -*-
from influxdb import InfluxDBClient
import yaml
import os
import time
import datetime
import uuid
from workcondition import models
import logging
import traceback
log = logging.getLogger("workcondition")


from django.shortcuts import render

from django.http import HttpResponse

class WorkCondition(object):
    def connect_influxdb(self, ip, port, username='', password=''):
        client = InfluxDBClient(ip, port, username, password)
        client._headers = {'Content-Type': 'application/json'}
        log.info(f"Connected influxdb host： {ip}:{port}, username：{username}, password：{password}")
        return client

    def remove_blank(self, key):
        if key is None:
            return ''
        else:
            return key.strip().replace(' ', '')
    def get_uuid(self):
        return uuid.uuid4().hex

    def yam(self):
        filename = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/monitor/config.yaml"
        f = open(filename, encoding='utf-8')
        res = yaml.load(f)
        return res

    def workcondition_config(self):
        return self.yam()['services']['monit_workcondition']

    def common_config(self):
        return self.yam()['database']

    def get_influxdb(self):
        return self.remove_blank(self.common_config()['influxdb'])

    def get_influxdb_user(self):
        return self.common_config()['influxdb_user']

    def get_cloudId(self):
        return self.remove_blank(self.workcondition_config()['cloudId'])

    def get_tenant(self):
        return self.remove_blank(self.workcondition_config()['tenantId'])

    def get_interval(self):
        return self.workcondition_config()['interval']

    def get_rule(self):
        rule = self.workcondition_config()['rule']
        return rule

    def unique_data(self, data):
        """
            保留最近一个时间段的数据
        """
        tenants = set([i[1] for i in data])
        unique_res = []
        for child in tenants:
            for j in data:
                if child == j[1]:
                    unique_res.append(j)
                    break
        return unique_res

    def transfer_stamp(self, time_str):
        timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        return timeStamp

    def deal_influxdb_time(self, now_time):
        return now_time.replace('T',' ').replace('Z','').split('+')[0]

    def in_this_time(self, now_time, begin, end):
        """
            判断时间在开始和结束区间内
            指定时间 开始时间 结束时间
        """
        today = str(datetime.date.today())
        begin_stamp = self.transfer_stamp(today+' '+begin)
        end_stamp = self.transfer_stamp(today+' '+end)
        compareTime =  self.transfer_stamp(today+' '+now_time.split(' ')[1])
        flag = True
        if compareTime < begin_stamp or compareTime > end_stamp:
            flag = False
        return flag

    def get_now_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def get_last_time(self,now_time, days=1):
        """
        获取最近days的 时间，如最近的一天（昨天），上周的同天
        """
        ymd = now_time.split(' ')[0]
        hms = now_time.split(' ')[1]
        ymd = datetime.date.fromisoformat(ymd)
        ymd = ymd - datetime.timedelta(days)
        return str(ymd) + ' '+ hms

    def exists_tenant(self, tenant, tenant_list):
        tenant_db = 'db_'+tenant
        if tenant_db not in tenant_list:
            log.error(f"tenant {tenant} is not exist in dbs")

    def is_in_interval(self):
        """
        判断是否在采集间隔期内
        test passed
        """
        latest_recordTime = self.get_latest_recordTime()
        now_time = self.get_now_time()
        flag = False
        if latest_recordTime == '':
            return False
        latest_recordTime = self.transfer_stamp(latest_recordTime)
        now_time = self.transfer_stamp(now_time)
        interval_time = self.get_interval()*60
        if now_time - latest_recordTime < interval_time:
            flag = True
        return flag

    def create_workcondition(self, row_dict):
        """
        落库采集到的工况数量
        test passed
        insert_row = {
            'cloudeid': get_cloudId(),
            'tenantid': 't2',
            'begintime': get_now_time(),
            'endtime': get_now_time(),
            'workingtime': get_now_time(),
            'totalnum': 66,
            'createtime': get_now_time()
        }
        res = create_workcondition(insert_row)
        """
        models.MonitWorkcondition.objects.create(**row_dict)
        log.info(f"Add row to monit_workcondition： {row_dict}")

    def create_alarm(self, row_dict):
        """
        创建告警
        test passed
        content = f"【过高报警】2020-11-06 14:38:00 租户t2 工况落库量50，" \
                  f"环比昨天（2020-11-06 14:38:00）工况落库量150，环比率33.33%" \
                  f"大于最大值20%"
        alarm_row = {
            'uuid': self.get_uuid(),
            'cloudeid': get_cloudId(),
            'tenantid': 't2',
            'modelid': '1122',
            'deviceid': '3344',
            'level': '0',
            'type': '工况落库量告警',
            'content': content,
            'rule': {type: 2,min: 50,max: 200 },
            'createtime': get_now_time()
        }
        res = create_alarm(alarm_row)
        """
        models.MonitEvent.objects.create(**row_dict)
        log.info(f"Add row to monit_event： {row_dict}")

    def get_last_data(self, tenantId, now_time, days=1):
        """
        mysql monit_storenum表返回数据
        res = [{'cloudeId':'public','tenantId':'t2','beginTime':'','EndTime':'','workingTime':'2020-11-03 18:00:00','totalNum':200,'createTime':''}]
        test passed
        """
        now_time = self.get_last_time(now_time, days)
        res = models.MonitWorkcondition.objects.filter(tenantid=tenantId,workingtime=now_time)
        res = list(res)
        return res

    def get_latest_recordTime(self):
        """
        获取本地工况表最近1条存储的工况时间记录
        test passed
        """
        res = models.MonitWorkcondition.objects.values('workingtime').order_by('-workingtime')[:1]
        res = list(res)
        res = [i['workingtime'].strftime("%Y-%m-%d %H:%M:%S") for i in res if i['workingtime']]
        if res.__len__()>0:
            return res[0]
        else:
            return ''

    def get_local_cache(self):
        """
        获取本地工况表最近10条存储的工况时间记录 order by workingTime desc limit 10
        test passed
        """
        res = models.MonitWorkcondition.objects.values('workingtime').order_by('-workingtime')[:10]
        res = list(res)
        res = [i['workingtime'].strftime("%Y-%m-%d %H:%M:%S") for i in res if  i['workingtime']]
        return res

    def compare_data(self, now_tenantT, row_time, value, yesterday_data, rule):
        """
        环比昨天或者环比上周
        租户 工况时间 工况值 历史数据（昨天、上周） 告警规则
        """

        if yesterday_data.__len__() > 0:
            compare_flag = '上周'
            if rule['type'] == 2:
                compare_flag = '昨天'
            min_value = rule['min']
            max_value = rule['max']
            level = rule['level']
            yesterday_value = yesterday_data[0].totalnum
            yesterday_workTime = yesterday_data[0].workingtime
            if yesterday_value > 0:
                yesterday_rate = (value / yesterday_value) * 100
                if yesterday_rate < min_value or yesterday_rate > max_value:
                    if yesterday_rate < min_value:
                        content = f"【过低报警】{row_time} 租户{now_tenantT} 工况落库量{value}，" \
                                  f"环比{compare_flag}（{yesterday_workTime}）工况落库量{yesterday_value}，环比率{yesterday_rate}%" \
                                  f"小于最小值{min_value}%"
                    else:
                        content = f"【过高报警】{row_time} 租户{now_tenantT} 工况落库量{value}，" \
                                  f"环比{compare_flag}（{yesterday_workTime}）工况落库量{yesterday_value}，环比率{yesterday_rate}%" \
                                  f"大于最大值{max_value}%"
                    alarm_row = {
                        'uuid': self.get_uuid(),
                        'cloudeid': self.get_cloudId(),
                        'tenantid': now_tenantT,
                        'modelid': '',
                        'deviceid': '',
                        'level': level,
                        'type': '工况落库量告警',
                        'content': content,
                        'rule': rule,
                        'createtime': self.get_now_time()
                    }
                    self.create_alarm(alarm_row)

    def rule_calculation(self, data, rules, beginTime, EndTime, local_cache=[]):
        """
            规则计算
            工况数据 告警规则
            data = [['2020-11-04T07:00:00Z', 't2', 49]]
            rule_calculation(data, get_rule())
        """
        for child in data:
            log.info(f"Processing data： {child}")
            value = child[2]
            row_time = self.deal_influxdb_time(child[0])
            now_tenantT = child[1]
            # 如果工况时间在本地缓存里，什么都不干
            if row_time in local_cache:
                break
            else:
                work_row ={
                    'cloudeid': self.get_cloudId(),
                    'tenantid': now_tenantT,
                    'begintime': beginTime,
                    'endtime': EndTime,
                    'workingtime': row_time,
                    'totalnum': value,
                    'createtime': self.get_now_time()
                }
                self.create_workcondition(work_row)

            for item in rules:
                min_value = item['min']
                max_value = item['max']
                level = item['level']
                if item['type'] == 1:
                    begin = item['begin']
                    end = item['end']
                    normal = item['normal']
                    if self.in_this_time(row_time, begin, end):
                        if value < min_value or value > max_value:
                            if value < min_value:
                                content = f"【过低报警】{row_time} 租户{now_tenantT} 工况落库量{value}，小于最小值{min_value} "
                            else:
                                content = f"【过高报警】{row_time} 租户{now_tenantT} 工况落库量{value}，大于最大值{max_value} "
                            alarm_row = {
                                'uuid': self.get_uuid(),
                                'cloudeid': self.get_cloudId(),
                                'tenantid': now_tenantT,
                                'modelid': '',
                                'deviceid': '',
                                'level': level,
                                'type': '工况落库量告警',
                                'content': content,
                                'rule': item,
                                'createtime': self.get_now_time()
                            }
                            self.create_alarm(alarm_row)

                elif item['type'] in [2,3]:
                    last_data = self.get_last_data(now_tenantT, row_time, 1)
                    self.compare_data(now_tenantT, row_time, value, last_data, item)
                    #【过低报警】{row_time} 租户A工况落库量{value} 环比昨天{row_time}<min_value
                    #【过高报警】{row_time} 租户A工况落库量{value} 环比昨天{row_time}>max_value
                    #环比昨天同一时间区间，报警条件为小于50%或者大于200%。

    def run(self):
        try:
            log.info(f"-----------------Begin monit workcondition-----------------")
            log.info(f"Get configuration information")
            influxdb_hosts = self.get_influxdb()
            monit_object_tenant = self.get_tenant()
            influxdb_hosts = influxdb_hosts.strip().replace(' ', '')
            monit_interval = str(self.get_interval())
            cloudId = self.get_cloudId()
            beginTime = self.get_now_time()
            result_list = []
            if self.is_in_interval():
                log.info(f"This collection is in the collection interval, do not perform any operation")
                return True
            if cloudId == '' and monit_object_tenant == '':
                log.error(f"cloudId and tenantId all is null, end this collection")
                return True
            if cloudId != '':
                monit_object_tenant = ''
            for host in influxdb_hosts.split(','):
                ip = host.split(':')[0]
                port = host.split(':')[1]
                influxdb_user = self.get_influxdb_user()
                username = ''
                password = ''
                if influxdb_user[0] is not None:
                    if influxdb_user.__len__() >1 and influxdb_hosts.split(',').__len__() > influxdb_user.__len__():
                        log.error(f"Don't support this configure influxdb_user, does not match influxdb host")
                        return True
                    username = self.remove_blank(influxdb_user[0].split('@')[0])
                    password = self.remove_blank(influxdb_user[0].split('@')[1])
                client = self.connect_influxdb(ip, port, username, password)
                dbs = [ tenant['name'] for tenant in client.get_list_database() ]
                log.info(f"Influxdb dbs is： {dbs}")
                monit_object_tenant = monit_object_tenant.strip().replace(' ', '')
                sql = 'SELECT  time,__deviceId__,__storageUsage__  FROM "type_usage_statistics" WHERE time > now() - ' + monit_interval + 'm  '
                tenant_list = monit_object_tenant.split(',')
                if monit_object_tenant != '' and tenant_list.__len__() > 0:
                    for key, value in enumerate(tenant_list):
                        if key == 0:
                            sql = sql + f" and "
                        else:
                            sql = sql + f" or "
                        sql = sql + f"  \"__deviceId__\" = '{value}' "
                        self.exists_tenant(value, dbs)

                sql = sql + " order by time desc  TZ('Asia/Shanghai');"
                log.info(f"Influxdb sql is： {sql}")
                result = client.query(sql, database='db_usage')
                series = result.raw['series']
                log.info(f"Collect working condition data： {series}")
                if series.__len__() > 0:
                    values = self.unique_data(series[0]['values'])
                    result_list = result_list + values
                    log.info(f"Working condition data after deduplication is： {result_list}")

            EndTime = self.get_now_time()
            local_cache = self.get_local_cache()
            if result_list.__len__() > 0:
                rules = self.get_rule()
                log.info(f"Start matching alarm rules")
                self.rule_calculation(result_list, rules, beginTime, EndTime, local_cache)
            else:
                log.info(f"Collect working condition data as： {result_list}，Do nothing")

        except Exception as e:
            errMes = f"Run failure exception, {str(e)}"
            log.error(errMes)
            log.error(traceback.format_exc())
        finally:
            log.info(f"-----------------End monit workcondition-----------------")



def test(request):
    wk = WorkCondition()
    wk.run()

    return HttpResponse("hello world!")

if __name__ == '__main__':
    pass

