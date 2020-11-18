import prometheus_client
from prometheus_client import Counter,Gauge
from prometheus_client.core import CollectorRegistry
from flask import Response, Flask
import queue
import sys
sys.path.append('..')
from  updata.models import AlarmDeviceTypeIdInstruntionDelay
from time import sleep


 
app = Flask(__name__)
q = queue(maxsize=10)
cmd = Gauge('monitor_instruction', 'alarm instruction delay', ['cloudName', 'uuid', 'tenantId'])

def cmd_producer(q):
    object1 = AlarmDeviceTypeIdInstruntionDelay.objects.earliest()
    id = object1.id
    while True:
        q.put(object1)
        sleep(300)
        id += 1
        object2 = AlarmDeviceTypeIdInstruntionDelay.objects.get(id=id)         
        if object2.DoesExist:
            if not q.full():
                q.put(object2)
            else:
                id = object1.id
        elif object2.DoesNotExist:
            id = object1.id
        

def metric_consumer(q):
    object2 = q.get()
    a = [object2.cloudName, object2.uuid, object2.tenantId]
    return a
    
 

@app.route('/metrics/instruction')
def index(q):
    a = metric_consumer(q)
    cmd.labels(a[0], a[1], a[2]).inc()
    return Response(prometheus_client.generate_latest(c),
                    mimetype="text/plain")
 
if __name__ == "__main__":
    cmd_producer(q)
    app.run(host="0.0.0.0")
