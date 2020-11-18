from . models import *
import prometheus_client
from prometheus_client import Counter,Gauge
from prometheus_client.core import CollectorRegistry
from time import sleep
from django.http import HttpResponse, response
import redis
import logging
from monitor.yamls import fetchConfig

logging = logging.getLogger("instruction")
CONFIG = fetchConfig("microscope")

pool = redis.ConnectionPool(
      host=CONFIG['redis']['host'], 
      port=CONFIG['redis']['port'], 
      password=CONFIG['redis']['passwd'], 
      db=3, 
      decode_responses=True
    )
r = redis.Redis(connection_pool=pool)

cmd = Gauge('monitor_instruction', 'alarm instruction delay', ['cloudName', 'uuid', 'tenantId', 
            "deviceTypeId", "isAlarm", "alarmLevel", "alarmInfo" ])

def get_redis_alarmId():
    try:
        r.setnx('instruction_id', '1')
        id = int(r.get("instruction_id"))
        id += 1
        object1 = AlarmDeviceTypeIdInstruntionDelay.objects.filter(id=id)
        if object1.exists():
            object2 = AlarmDeviceTypeIdInstruntionDelay.objects.get(id=id)
            i = [
                object2.cloudName, 
                object2.uuid, 
                object2.tenantId, 
                object2.deviceTypeId,
                object2.isAlarm,
                object2.alarmLevel,
                object2.alarmInfo
                ]
            cmd.labels(i[0],i[1],i[2],i[3],i[4],i[5],i[6])
            logging.info("get_redis_alarmId obtain {0} {1}".format(i, id))  
            r.set("instruction_id", str(id))
            return prometheus_client.generate_latest(cmd)
        else:
            id -= 1
            r.set("instruction_id", str(id))
            i = [0,0,0,0,0,0,0]
            logging.info("get_redis_alarmId obtain {0} {1}".format(i, id))
            cmd.labels(i[0],i[1],i[2],i[3],i[4],i[5],i[6]).inc()
            return prometheus_client.generate_latest(cmd)
    except Exception as e:
        logging.error(repr(e))
        return repr(e)



