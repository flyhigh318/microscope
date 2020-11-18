
from pymongo import MongoClient
import datetime, time, json, sys
import logging 
import asyncio
from . models import InstrutionDelay
from . yamls import store_config 
MONGOACL1 = store_config()
MONITORINSTRUTION = store_config(params="instruction")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

class Instrution(object):

    def __init__(self):
        pass
    
    def getClient(self, **kwargs):
        client = MongoClient(kwargs['url'],
                      username=kwargs['user'],
                      password=kwargs['passwd'],
                      authSource=kwargs['authSource'],
                      authMechanism=kwargs['authMechanism'],
                      maxPoolSize=10)
        return client

    def unixMilsecondes(self):
        return int(time.mktime(datetime.datetime.now().timetuple()) * 1000)

    def getAllDeviceTypeIdByTenantId(self, tenantId, db="metadata", col="DeviceStatus", **MONGOACL):
        client = self.getClient(**MONGOACL)
        mydb = client[db]
        mycol = mydb[col]
        query = {
            "tenantId": tenantId,
            "online" : False,
        }
        show_fields = {
            "tenantId": 1,
            "deviceTypeId": 1, 
            "deviceId": 1,
            "_id": 0
        }
        device_type_id_count = mycol.find(query).count()
        print(device_type_id_count)
        i = 0
        # for device_type_tenant in mycol.find(query, show_fields).distinct("deviceTypeId"):
        for device_type_tenant in mycol.find(query, show_fields).sort("deviceTypeId", -1):
            i = i + 1
            logging.debug(" ... is doing No: {0} device_type_id {1}".format(i, device_type_tenant))
            yield device_type_tenant, i

    def getDeviceIdByDeviceTypeIdTenantId(self, tenantId, deviceTypeId, db="metadata", col="DeviceStatus", **MONGOACL):
        client = self.getClient(**MONGOACL)
        mydb = client[db]
        mycol = mydb[col]
        query = {
            "online" : True,
            "deviceTypeId" : deviceTypeId,
            "tenantId" :     tenantId,
        }
        show_fields = {
            "deviceId": 1, 
            "deviceTypeId": 1,
            "tenantId": 1,
            "_id": 0
        }
        device_count = mycol.find(query).limit(1)
        if len(list(device_count)) == 0:
            logging.info("getDeviceIdByDeviceTypeIdTenantId TenantId {0} DeviceTypeId {1} devices numbers: {2}".format(tenantId, deviceTypeId, 0))
        else:
            device_count = mycol.find(query).count()
            logging.info("getDeviceIdByDeviceTypeIdTenantId TenantId {0} DeviceTypeId {1} devices numbers: {2}".format(tenantId, deviceTypeId, device_count))
        for device in mycol.find(query, show_fields).sort("deviceTypeId", -1):
            logging.debug("getDeviceIdByDeviceTypeIdTenantId obtain {}".format(device))
            yield device
        
    def getDeviceRequestMsgByDeviceId(self, tenantId, deviceTypeId, interval=10, db="metadata", col="DeviceRequestMsg", **MONGOACL):
        """
        :returns:
            yield: show_fields
        """
        client = self.getClient(**MONGOACL)    
        mydb = client[db]
        mycol = mydb[col]
        for device in self.getDeviceIdByDeviceTypeIdTenantId(tenantId, deviceTypeId, **MONGOACL):
            query = {
                # "updateTime": {"$exists": True},
                # "sendTime": {"$exists": True},
                # "ts": {"$exists": True},
                "deviceId": device['deviceId'],
                "tenantId": device['tenantId'],
                # "expired" : False, 
                # "instructionType" : "LIVE",                
            }
            show_fields = {
                "expired" :1,
                "groupId": 1,
                "_id" : 1,
                "msgId" : 1,
                "deviceId" : 1,
                "phase" : 1,
                "instructionId" : 1,
                "priority" : 1,
                "deviceUserName" : 1,
                "created" : 1,
                "createdBy" : 1,
                "tenantId" : 1,
                "errorMsg" : 1,
                "ts" : 1,
                "sendTime": 1,
                "updateTime" : 1
            }
            # for device_request_msg in mycol.find(query, show_fields).sort("sendTime" , -1):
            # for device_request_msg in mycol.find(query, show_fields).sort("updateTime" , -1):
            deviceIsInDeviceRequestMsg = mycol.find(query,show_fields).limit(1)
            if len(list(deviceIsInDeviceRequestMsg)) == 0:
                logging.info("getDeviceRequestMsgByDeviceId TenantId {0} DeviceTypeId {1} devices {2} is not in deviceRequestMsg, number is 0".format(tenantId, deviceTypeId, device['deviceId']))
                continue
            for device_request_msg in mycol.find(query, show_fields).sort("deviceId", -1):
                if "expired" in device_request_msg.keys():
                    if device_request_msg['expired'] == True:
                        logging.info("getDeviceRequestMsgByDeviceId skip {} due to expired true".format(device_request_msg))
                        continue
                # if "updateTime"  in device_request_msg.keys():
                if "sendTime"  in device_request_msg.keys():
                   timestamp = self.unixMilsecondes()
                #    if timestamp - int(device_request_msg["updateTime"]) > 10 * 24 * 3600 * 1000:
                   if timestamp - int(device_request_msg["sendTime"]) < interval * 60 * 1000:
                       logging.debug("getDeviceRequestMsgByDeviceId obtain  {0} minitues device_request_msg {1}".format(interval, device_request_msg))
                       yield device_request_msg
                   else:
                       logging.info("getDeviceRequestMsgByDeviceId obtain  {0} minitues not satify device_request_msg {1}".format(interval, device_request_msg)) 
                       continue
                else:
                    logging.debug("getDeviceRequestMsgByDeviceId there is no sendTime key in device_request_msg, detailed as below: {}, continue".format(device_request_msg))
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
        for device_request_msg in self.getDeviceRequestMsgByDeviceId(tenantId, deviceTypeId,**MONGOACL):
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
                # if device_request_msg['ts'] - device_request_msg['sendTime'] > device_request_attribue['timeout']:
                if device_request_msg['ts'] - device_request_msg['updateTime'] < device_request_attribue['timeout']:
                    find_device_flag = 0
                    for device_complex in ret:
                        for device in device_complex.keys():
                            if device == device_request_msg['deviceId']:
                               device_complex[device_request_msg['deviceId']]['timeoutCount'] = device_complex[device_request_msg['deviceId']]['timeoutCount'] + 1 
                               if len(device_complex[device_request_msg['deviceId']]['deviceRequestMsgId']) < 5:
                                  device_complex[device_request_msg['deviceId']]['deviceRequestMsgId'].append(device_request_msg['_id'])
                               find_device_flag = 1
                               break
                        if find_device_flag == 1:
                            break                  
        logging.debug("getGroupIdByDeviceRequestMsg info: {}".format(ret))
        return json.dumps(ret, ensure_ascii=False) 

    def getAlarmInfo(self,alarm_cmd_percent, alarm_device_percent, ret):
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
        timeout_device_set = set()
        all_device_set = set()
        for device_complex in ret:
            logging.info(device_complex)
            for device in device_complex.keys():
                ts1 = device_complex[device]['timeoutCount'] 
                ts2 = device_complex[device]['cmdCount']
                if ts1 / ts2 * 100 > alarm_cmd_percent:
                    timeout_device_set.add(device)
                all_device_set.add(device)      
        if len(timeout_device_set) / len(all_device_set) * 100  > alarm_device_percent:
            return timeout_device_set
        else:
            timeout_device_set = set()
            return timeout_device_set

    def insertAlarmInfoModels(self, timeout_device_set): 
        InstrutionDelay.objects.create(**info)            

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
        client = self.getClient(**MONGOACL1)
        mydb = client[db]
        mycol = mydb[col]
        query = {
            "tenantId": tenantId,
        }
        # query = {
        #     "_id": db.Tenant.findOne({'tenantId' : tenantId }).hub.$id,
        # }
        show_fields = {
            "tenantId" : 1,
            "tenantType" : 1,
            "hub" : 1
        }
        hub = {}
        if mycol.find(query, show_fields).count() == 0:
            logging.error("findTenantOnHubServiceDescription:  can't find tenantId {}, please check".format(tenantId))
            return hub
        for tenant in mycol.find(query, show_fields):
        # for tenant in mycol.findOne({"_id": db.Tenant.findOne({'tenantId' : tenantId }).hub.$id}):
            hub_dbref = tenant['hub']
            hub["$id"] = str(hub_dbref).split("(")[1].split(")")[0].split(',')[1].split(" ")[1].strip("'")
            hub["$ref"] = str(hub_dbref).split("(")[1].split(")")[0].split(',')[0].strip("'")
            # logging.info(hub["$id"])
            logging.debug("findTenantOnHubServiceDescription obtain hub {}".format(hub))
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
        # hubdescription = mycol.find(query, show_fields) 
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

def handleDeviceType():  
    logging.info("start handle device type Id: hello, world! have a nice day")
    logging.debug(MONGOACL1)
    logging.debug(MONITORINSTRUTION['teanantId__deviceTypeId'])
    alarm_cmd_percent = MONITORINSTRUTION['alarm_cmd_percent']
    alarm_device_percent = MONITORINSTRUTION['alarm_device_percent']
    for tenant_devicetype in MONITORINSTRUTION['teanantId__deviceTypeId'].split(','):       
        tenantId = str(tenant_devicetype.split("__")[0]).strip()
        deviceTypeId = str(tenant_devicetype.split("__")[1]).strip()
        logging.debug("obtain tenantId {0} and deviceTypeId {1}".format(tenantId, deviceTypeId))
        device = Instrution()
        startTime = device.unixMilsecondes()
        hub = device.findTenantOnHubServiceDescription(tenantId)
        if hub:
           MONGOACL = device.findMongoAclOnHubServer(hub)
           result = device.getGroupIdByDeviceRequestMsg(tenantId, deviceTypeId, **MONGOACL)
           logging.info(result)
           endTime = device.unixMilsecondes()
           result = json.loads(result)
           if len(result) == 0:
               continue
           alarm_device_set = device.getAlarmInfo(alarm_cmd_percent,alarm_device_percent, result)
           result = list(alarm_device_set)
           result.append( 
               {
                 "startTime": startTime,
                 "endTime": endTime
               }
           )
        #    logging.info(json.dumps(alarm_device_set, ensure_ascii=False))        
        else:
           logging.warn("skip tenantId: {}".format(tenantId))
