#!/usr/bin/env python
# encoding: utf-8

import ConfigParser


class Config:
    dailyConfigPath = "./config/daily/config.property"
    prepubConfigPath = "./config/prepub/config.property"
    publishConfigPath = "./config/publish/config.property"
    cf = ConfigParser.ConfigParser()
    env = "daily"

    def __init__(self, env="daily"):
        self.env = env
        configPath = self.getConfigPath()
        self.cf.read(configPath)

    def getConfigPath(self):
        if(self.env == "publish"):
            return self.publishConfigPath
        elif (self.env == "prepub"):
            return self.prepubConfigPath
        else:
            return self.dailyConfigPath

    def getValue(self, section, key):
        return self.cf.get(section, key)

    def getSections(self):
        return self.cf.sections()

if __name__ == "__main__":
    config = Config("daily")
    #print(config.cf.sections())
    print(config.getValue("db", "test"))
