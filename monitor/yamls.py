import yaml
import os
from pathlib import Path

BASE_DIR_1 = Path(__file__).resolve(strict=True).parent

class Yamls(object):

    def __init__(self):
        pass

    def loadYaml(self):
        filename = str(BASE_DIR_1) + "/config.yaml"
        f = open(filename, encoding='utf-8')
        res = yaml.safe_load(f)
        f.close()
        return res

    def getConfig(self, params="mongo"):
        if params == "mongo":
           return self.loadYaml()['database']['mongodb']
        elif params == "instruction":
           return self.loadYaml()['services']['monit_instruction']
        elif params == "microscope":
           return self.loadYaml()["microscope"]["database"]

def fetchConfig(params):
    instance1 = Yamls()
    return instance1.getConfig(params=params)    

