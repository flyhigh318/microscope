
from pymongo import MongoClient
import datetime, time, json, sys, uuid
import logging 
import asyncio
from . models import *
from monitor import fetchConfig
MONGOACL1 = fetchConfig("mongo")
MONITORINSTRUTION = fetchConfig("instruction")
logging = logging.getLogger("instruction")

class Instrution(object):

    def __init__(self):
        pass
    
    def getClient(self, **kwargs):
        """
        :prames:
           kwargs:
        :return:
           client
        """
        client = MongoClient(kwargs['url'],
                      username=kwargs['user'],
                      password=kwargs['passwd'],
                      authSource=kwargs['authSource'],
                      authMechanism=kwargs['authMechanism'],
                      maxPoolSize=10)
        return client

    def unixMilsecondes(self):
        return int(time.mktime(datetime.datetime.now().timetuple()) * 1000)
    
    def timeStamp(self):
        datetime1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return datetime1

    def getDeviceTypeIdByDeviceIdTenantId(self, tenantId, deviceId, db="metadata", col="DeviceStatus", **MONGOACL):
        """
        :params:
           tenantId:
           deviceId:
        :returns:  onlines devices,one dict,including keys:tenantId, deviceTypeId, deviceId
          {
            tenantId: xx,
            deviceTypeId: xx,
            deviceId: xx
          }
        """
        client = self.getClient(**MONGOACL)
        mydb = client[db]
        mycol = mydb[col]
        query = {
            "online" : True,
            "deviceId" : deviceId,
            "tenantId" : tenantId,
        }
        show_fields = {
            "deviceId": 1, 
            "deviceTypeId": 1,
            "tenantId": 1,
            "_id": 0
        }
        device_count = mycol.find(query).count()
        logging.info("getDeviceIdByDeviceTypeIdTenantId TenantId {0} DeviceId {1} deviceTypeId numbers: {2}".format(tenantId, deviceId, device_count))
        for devicetypeid in mycol.find(query, show_fields):
            logging.debug("getDeviceTypeIdByDeviceIdTenantId obtain {}".format(devicetypeid))
            yield devicetypeid      

    def getDeviceRequestMsgByDeviceTypeIdTenantId(self, tenantId, deviceTypeId, interval=10, db="metadata", col="DeviceRequestMsg", **MONGOACL):
        """
        :params:
           tenantId:
           deviceTypeId:
        :returns:
            yield: show_fields
        """
        client = self.getClient(**MONGOACL)    
        mydb = client[db]
        mycol = mydb[col]
        # now = self.unixMilsecondes()
        now = 1601004265877 
        before = now - interval * 60 * 1000
        query = {
            # "updateTime": {"$exists": True},
            # "sentTime": {"$exists": True},
            # "ts": {"$exists": True},
            "tenantId": tenantId,
            "deviceTypeId": deviceTypeId, 
            # "expired" : False, 
            # "instructionType" : "LIVE",  
            "sentTime": {"$gte": before, "$lte": now},             
        }
        show_fields = {
            "expired" :1,
            "groupId": 1,
            "_id" : 1,
            # "msgId" : 1,
            "deviceId" : 1,
            "deviceTypeId":1,
            # "phase" : 1,
            # "instructionId" : 1,
            # "priority" : 1,
            # "deviceUserName" : 1,
            # "created" : 1,
            # "createdBy" : 1,
            "tenantId" : 1,
            # "errorMsg" : 1,
            "ts" : 1,
            "sentTime": 1,
            # "updateTime" : 1
        }
        logging.info("getDeviceRequestMsgByDeviceTypeIdTenantId start to handle tenantId {0} and deviceTypeId {1}".format(tenantId,deviceTypeId))
        i = 0
        num = mycol.find(query, show_fields, batch_size=10000).sort("sentTime", -1).count()
        logging.info("getDeviceRequestMsgByDeviceTypeIdTenantId query numbers is {}".format(num))
        for device_request_msg in mycol.find(query, show_fields, batch_size=10000).sort("sentTime", -1):
            i += 1
            logging.info("getDeviceRequestMsgByDeviceTypeIdTenantId is doing instrution number: {}".format(i))
            if "sentTime"  in device_request_msg.keys():
                # if device_request_msg['ts'] ==0:
                #     logging.info("getDeviceRequestMsgByDeviceTypeIdTenantId device_request_msg['ts'] equal 0")
                #     continue
                yield device_request_msg
                # if device_request_msg["tenantId"] == tenantId:                    
                #     yield device_request_msg
                #     deviceId = device_request_msg['deviceId']
                #     for devicetypeid in self.getDeviceTypeIdByDeviceIdTenantId(tenantId, deviceId, **MONGOACL):
                #         if devicetypeid['deviceTypeId'] == deviceTypeId and \
                #             devicetypeid['online'] == True:
                #            device_request_msg['device'] = deviceTypeId
                #            yield device_request_msg
            else:
                logging.debug("getDeviceRequestMsgByDeviceTypeIdTenantId there is no sendTime key in \
                device_request_msg, detailed as below: {}, continue".format(device_request_msg))
                continue
                       
    def getGroupIdByDeviceRequestMsg(self, tenantId, deviceTypeId, db="metadata", col="DeviceRequestAttribute", **MONGOACL):
        """
        :parames:
           teantId:
           deviceTypeId:
        :return:
            ret: [
                {
                    deviceId0: {
                        tenantId: '5eadf1212ff',
                        deviceTypeId: 'bum',
                        cmdCount: 100,
                        timeoutCount: 50
                        deviceRequestMsgId: [
                           "_id1",
                           "_id2"
                        ]
                    }
                },
                {},
            ]
        """                      
        client = self.getClient(**MONGOACL)    
        mydb = client[db]
        mycol = mydb[col]
        ret = []
        for device_request_msg in self.getDeviceRequestMsgByDeviceTypeIdTenantId(tenantId, deviceTypeId,**MONGOACL):
            loop_time_ret = 0
            find_device_flag = 0
            if len(ret) != 0 :
                for device_complex in ret:
                    loop_time_ret = loop_time_ret + 1
                    for device in device_complex.keys():
                        if device == device_request_msg['deviceId']:
                           device_complex[device_request_msg['deviceId']]['cmdCount'] = device_complex[device_request_msg['deviceId']]['cmdCount'] + 1
                           find_device_flag = 1
                           break               
                if len(ret) == loop_time_ret and find_device_flag == 0:
                   logging.info(device_request_msg)
                   ret1 = {}                  
                   ret1[device_request_msg['deviceId']] = {}
                   ret1[device_request_msg['deviceId']]['tenantId'] = device_request_msg['tenantId']
                   ret1[device_request_msg['deviceId']]['deviceTypeId'] = deviceTypeId
                   ret1[device_request_msg['deviceId']]['cmdCount'] = 1
                   ret1[device_request_msg['deviceId']]['timeoutCount'] = 0
                   ret1[device_request_msg['deviceId']]['deviceRequestMsgId'] = []
                   ret.append(ret1)                      
            else:
                ret1 = {}
                ret1[device_request_msg['deviceId']] = {}
                ret1[device_request_msg['deviceId']]['tenantId'] = device_request_msg['tenantId']
                ret1[device_request_msg['deviceId']]['deviceTypeId'] = deviceTypeId
                ret1[device_request_msg['deviceId']]['cmdCount'] = 1
                ret1[device_request_msg['deviceId']]['timeoutCount'] = 0
                ret1[device_request_msg['deviceId']]['deviceRequestMsgId'] = []
                ret.append(ret1)
            query = {
                "groupId": device_request_msg['groupId'],
                "tenantId": tenantId,
                "timeout": {"$gt": 0}
            }
            show_fields = {
                "groupId": 1,
                "_id" : 0,
                "timeout": 1
            }
            # logging.info("getGroupIdByDeviceRequestMsg  device_request_msg: {}".format(device_request_msg))
            for device_request_attribue in mycol.find(query, show_fields):
                if device_request_msg['ts'] - device_request_msg['sentTime'] < device_request_attribue['timeout']:
                    find_device_flag = 0
                    for device_complex in ret:
                        for device in device_complex.keys():
                            if device == device_request_msg['deviceId']:
                               device_complex[device_request_msg['deviceId']]['timeoutCount'] = device_complex[device_request_msg['deviceId']]['timeoutCount'] + 1 
                               if len(device_complex[device_request_msg['deviceId']]['deviceRequestMsgId']) < 3:
                                  device_complex[device_request_msg['deviceId']]['deviceRequestMsgId'].append(device_request_msg['_id'])
                               find_device_flag = 1
                               break
                        if find_device_flag == 1:
                            break                  
        logging.debug("getGroupIdByDeviceRequestMsg info: {}".format(ret))
        return json.dumps(ret, ensure_ascii=False) 

    def insertDevicesInstrutionDelayModels(self, alarmId, startTime, endTime, result):
        """
        :params:
            result: [
                {
                    deviceId0: {
                        tenantId: '5eadf1212ff',
                        deviceTypeId: 'bum',
                        cmdCount: 100,
                        timeoutCount: 50
                        deviceRequestMsgId: [
                           "_id1",
                           "_id2"
                        ]
                    }
                },
                {},
            ]

           info: {
               alarmId:
               cloudName:
               tenantId:
               deviceTypeId:
               deviceId:
               cmdRunCount:
               cmdTimeoutCount:
               deviceRequestMsgIds:               
               beginTime:
               endTime:
               createTime:
           }

        """
        if len(result) != 0:
            for device_complex in result:
               logging.info(device_complex)
               deviceId = list(device_complex.keys())[0]
               info = {
                   "alarmId":  AlarmDeviceTypeIdInstruntionDelay.objects.get(uuid=alarmId),
                   "cloudName": MONITORINSTRUTION['cloudName'],
                   "tenantId": device_complex[deviceId]['tenantId'],
                   "deviceTypeId": device_complex[deviceId]['deviceTypeId'],
                   "deviceId": deviceId,
                   "beginTime": int(startTime),
                   "endTime": int(endTime),
                   "cmdRunCount": device_complex[deviceId]['cmdCount'],
                   "cmdTimeoutCount": device_complex[deviceId]['timeoutCount'],
                   "deviceRequestMsgIds": json.dumps(device_complex[deviceId]['deviceRequestMsgId'], ensure_ascii=False),
                   "createTime": self.timeStamp()
               }
               DevicesInstrutionDelay.objects.create(**info)

    def getAlarmInfo(self, alarmId):
        """
        :parames:
            ret: [
                {
                    deviceId0: {
                        tenantId: '5eadf1212ff',
                        deviceTypeId: 'bum',
                        cmdCount: 100,
                        timeoutCount: 50
                        deviceRequestMsgId: [
                           "_id1",
                           "_id2"
                        ]
                    }
                },
                {},
            ]
        :returns:
            timeout_device_set: ret
        """
        object2 = AlarmDeviceTypeIdInstruntionDelay.objects.get(uuid=alarmId)
        
    def insertAlarmDeviceTypeIdInstruntionDelayModels(self, **info): 
        """
        :params:
          info: {
               uuid:
               cloudName:
               tenantId:
               deviceTypeId: 
               ruleInterval:
               ruleDevicesDelayRatio:
               ruleCmdDelayRatio:
               existCmdDeviceId:
               runCmdDeviceCount:
               timeoutCmdDeviceCount:
               isAlarm:
               alarmInfo:
               createTime:
          }
        :return:
           alarmId
        """
        AlarmDeviceTypeIdInstruntionDelay.objects.create(**info)
        alarmId = AlarmDeviceTypeIdInstruntionDelay.objects.get(uuid=info['uuid']) 
        return alarmId.uuid           

    def updateAlarmInfoModels(self,alarmId_id):
        alarmInfoTemplate = """
        告警项目： 模型指令延迟
        告警等级:  P{0}
        云名信息： {1}
        租户信息： {2}
        模型信息： {3}
        模型延迟率:{4}%
        告警码信息:{5}
        """
        level = MONITORINSTRUTION['alarm']['deviceTypeId']['level']
        object1 = AlarmDeviceTypeIdInstruntionDelay.objects.get(uuid=alarmId_id)
        if object1.existCmdDeviceId == True:
            runCmdDeviceCount = DevicesInstrutionDelay.objects.filter(alarmId_id=object1.id).count()
            timeoutCmdDeviceCount = 0
            isAlarm = False
            alarmLevel = 4
            alarmInfo = ""
            for i in DevicesInstrutionDelay.objects.filter(alarmId_id=object1.id):
                if int(i.cmdTimeoutCount / i.cmdRunCount * 100) >= object1.ruleCmdDelayRatio:
                    timeoutCmdDeviceCount += 1
            deviceTypeIdDelayRatio = int(timeoutCmdDeviceCount/runCmdDeviceCount * 100)
            if  deviceTypeIdDelayRatio >= object1.ruleDevicesDelayRatio:
                isAlarm = True
                if deviceTypeIdDelayRatio >= level['p0']['value']:
                    alarmLevel = 0
                    alarmInfo = alarmInfoTemplate.format(
                                alarmLevel, 
                                object1.cloudName,
                                object1.tenantId, 
                                object1.deviceTypeId,
                                deviceTypeIdDelayRatio,
                                object1.uuid)
                elif deviceTypeIdDelayRatio >= level['p1']['value']:
                    alarmLevel = 1
                    alarmInfo = alarmInfoTemplate.format(
                                alarmLevel, 
                                object1.cloudName,
                                object1.tenantId, 
                                object1.deviceTypeId,
                                deviceTypeIdDelayRatio,
                                object1.uuid)
            AlarmDeviceTypeIdInstruntionDelay.objects.filter(uuid=alarmId_id).update(
                runCmdDeviceCount=runCmdDeviceCount,
                timeoutCmdDeviceCount=timeoutCmdDeviceCount,
                isAlarm=isAlarm,
                alarmLevel=alarmLevel,
                alarmInfo=alarmInfo
            )    

    def findTenantOnHubServiceDescription(self, tenantId, db="metadata", col="Tenant"):
        """
        Tenant:
        {
           "_id" : "38fb2a08",
           "tenantId" : "38fb2a08",
           "tenantType" : "PRIVATE",
           "hub" : {
               "$ref" : "HubServiceDescription",
               "$id" : "5349b4ddd2781d08c09890f3"
           }
        }
        :returns:
            hub
        """
        try:
            hub = {}
            query = {
                "tenantId": tenantId,
            }
            show_fields = {
                "tenantId" : 1,
                "tenantType" : 1,
                "hub" : 1
            }
            client = self.getClient(**MONGOACL1)
            mydb = client[db]
            mycol = mydb[col]            
            if mycol.find(query, show_fields).count() == 0:
                logging.error("findTenantOnHubServiceDescription:  can't find tenantId {}, please check".format(tenantId))
            else:
                for tenant in mycol.find(query, show_fields):
                    logging.info(tenant)
                    if 'hub' in tenant.keys():
                        hub_dbref = tenant['hub']
                        hub["$id"] = str(hub_dbref).split("(")[1].split(")")[0].split(',')[1].split(" ")[1].strip("'")
                        hub["$ref"] = str(hub_dbref).split("(")[1].split(")")[0].split(',')[0].strip("'")
                        logging.info(hub["$id"])
                        logging.debug("findTenantOnHubServiceDescription obtain hub {}".format(hub))
                    else:
                        logging.error("findTenantOnHubServiceDescription there is no keys hub in tenant,as detailed: {}".format(tenant))
        except Exception as e:
            logging.error(repr(e))
        finally:
            return hub

    def findMongoAclOnHubServer(self, hub, db="metadata", col="HubServiceDescription"):
        """
        HubServiceDescription:
        {
          "_id" : "5349b4ddd2781d08c09890f3",
          "className" : "com.rootcloud.platform.models.deployment.HubServiceDescription",
          "mongo" : {
              "mode" : "replica",
              "nodeNum" : 3.0,
              "eachNodeCores" : 2.0,
              "eachNodeMemory" : 4.0,
              "eachNodeDisk" : 0.0,
              "initScriptUri" : "",
              "accessUrl" : "Testuser:Testuser4@10.70.40.10:27017,10.70.40.42:27017,10.70.40.12:27017",
              "type" : "mongo",
              "resourceLevel" : "shared",
              "version" : "1.0"
          },
          "emq" : {
              "emqServerUrl" : "10.70.40.124:1883,10.70.40.81:1883",
              "type" : "emq",
              "resourceLevel" : "shared",
              "version" : "1.0"
          },
          "kafka" : {
              "kafkaBroadcastAddress" : "10.70.40.140:9092",
              "type" : "kafka",
              "resourceLevel" : "shared",
              "version" : "1.0"
          },
          "type" : "hub",
          "tenantId" : "38fb2a08",
          "tier" : "shared",
          "projectCode" : "codeId",
          "projectName" : "name",
          "createdAt" : ISODate("2020-02-28T12:00:00.000Z"),
          "status" : 0,
          "statusDesc" : ""
        }
        
        : parames:
            "hub" : {
               "$ref" : "HubServiceDescription",
               "$id" : "5349b4ddd2781d08c09890f3"
           }
        : returns:
            MONGOACL
        """
        client = self.getClient(**MONGOACL1)
        mydb = client[db]
        mycol = mydb[col]
        query = {
            "_id": hub["$id"],
        }
        show_fields = {
            "mongo" : 1,
            "emq" : 1,
            "kafka" : 1,
            "type" : 1,
            "tenantId" : 1,
        }    
        logging.debug("findMongoAclOnHubServer query: {}".format(query))
        MONGOACL = {}   
        for hubdescription in mycol.find(query, show_fields):   
            logging.debug("findMongoAclOnHubServer hubdescription: {}".format(hubdescription))  
            hub_tmp_list = hubdescription['mongo']['accessUrl'].split('@')
            url = hub_tmp_list[1]
            user = hub_tmp_list[0].split(":")[0]
            password = hub_tmp_list[0].split(":")[1]
            MONGOACL = {
                    "url": url,
                    "user": user,
                    "passwd": password,
                    "authSource": "admin",
                    "authMechanism": "SCRAM-SHA-256"
            } 
            logging.debug("findMongoAclOnHubServer obtain mongoacl {}".format(MONGOACL))
        return MONGOACL  

def handleDeviceTypeTest():  
    logging.info("start handle device type Id: hello, world! have a nice day")
    logging.debug(MONGOACL1)
    logging.debug(MONITORINSTRUTION['teanantId__deviceTypeId'])
    alarm_dict = MONITORINSTRUTION['rules']
    logging.info(alarm_dict)
    cloudName = MONITORINSTRUTION['cloudName']   
    for tenant_devicetype in MONITORINSTRUTION['teanantId__deviceTypeId'].split(','): 
        try: 
            alarmId = uuid.uuid4().hex   
            tenantId = str(tenant_devicetype.split("__")[0]).strip()
            deviceTypeId = str(tenant_devicetype.split("__")[1]).strip()
            logging.debug("obtain tenantId {0} and deviceTypeId {1}".format(tenantId, deviceTypeId))
            device = Instrution()
            startTime = device.unixMilsecondes()/1000
            hub = device.findTenantOnHubServiceDescription(tenantId)
            alarm_dict['uuid'] = alarmId
            alarm_dict['tenantId'] = tenantId
            alarm_dict['deviceTypeId'] = deviceTypeId
            alarm_dict['cloudName'] = cloudName
            if hub:
               MONGOACL = device.findMongoAclOnHubServer(hub)
               result = device.getGroupIdByDeviceRequestMsg(tenantId, deviceTypeId, **MONGOACL)
               endTime = device.unixMilsecondes()/1000
               logging.info("handleDeviceType finish to handle getGroupIdByDeviceRequestMsg tenantId {0} deviceTypeId {1}, info:{2}"\
                   .format(tenantId, deviceTypeId, result))
               result = json.loads(result)
               if len(result) == 0:
                   alarm_dict['existCmdDeviceId'] = False
                   alarm_dict['createTime'] = device.timeStamp()
                   alarm_dict['updateTime'] = alarm_dict['createTime']
                   logging.debug(alarm_dict)
                   device.insertAlarmDeviceTypeIdInstruntionDelayModels(**alarm_dict)
                   continue
               else:
                  alarm_dict['existCmdDeviceId'] = True
                  alarm_dict['createTime'] = device.timeStamp()
                  alarm_dict['updateTime'] = alarm_dict['createTime']
                  alarmId = device.insertAlarmDeviceTypeIdInstruntionDelayModels(**alarm_dict) 
                  device.insertDevicesInstrutionDelayModels(alarmId, startTime, endTime, result) 
                  device.updateAlarmInfoModels(alarmId)          
                  logging.info(json.dumps(result, ensure_ascii=False))        
            else:
               logging.warn("skip tenantId: {}".format(tenantId))
        except Exception as e:
            logging.error(repr(e))