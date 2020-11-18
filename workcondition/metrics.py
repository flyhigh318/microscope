from workcondition import models
import prometheus_client
from prometheus_client import Counter,Gauge
import redis
import logging
from monitor import fetchConfig

logging = logging.getLogger("workcondition")
CONFIG = fetchConfig("microscope")

pool = redis.ConnectionPool(
      host=CONFIG['redis']['host'], 
      port=CONFIG['redis']['port'], 
      password=CONFIG['redis']['passwd'], 
      db=3, 
      decode_responses=True
    )
r = redis.Redis(connection_pool=pool)

cmd = Gauge('monitor_workcondition', 'alarm workcondition', ['cloudName', 'uuid', 'tenantId'
    , "isAlarm", "alarmLevel", "alarmInfo" ])

def get_redis_alarmId():
    try:
        r.setnx('workcondition_id', '1')
        id = int(r.get("workcondition_id"))
        id += 1
        object1 = models.MonitEvent.objects.filter(id=id)
        if object1.exists():
            object2 = models.MonitEvent.objects.get(id=id)
            i = [
                object2.cloudeid,
                object2.uuid, 
                object2.tenantid,
                0,
                object2.level,
                object2.content
                ]
            cmd.labels(i[0],i[1],i[2],i[3],i[4],i[5])
            logging.info("get_redis_alarmId obtain {0} {1}".format(i, id))  
            r.set("workcondition_id", str(id))
            return prometheus_client.generate_latest(cmd)
        else:
            id -= 1
            r.set("workcondition_id", str(id))
            i = [0,0,0,0,0,0,0]
            logging.info("get_redis_alarmId obtain {0} {1}".format(i, id))
            cmd.labels(i[0],i[1],i[2],i[3],i[4],i[5]).inc()
            return prometheus_client.generate_latest(cmd)
    except Exception as e:
        logging.error(repr(e))
        return repr(e)