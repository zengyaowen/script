#!/usr/bin/env python
# encoding: utf-8

import common.db
import datetime
import sys
from common.config import Config

def initDB(ip, dbname, name, pwd):
    return common.db.Connection(ip, dbname, name, pwd, True, 'utf8mb4')

if __name__ == "__main__":
    COMPANYUSERID = 0
    env = sys.argv[0]
    config = Config(env)
    ip = config.getValue("db", "ip")
    username = config.getValue("db", "username")
    databaseName = config.getValue("db", "database")
    password = config.getValue("db", "password")
    conn = initDB(ip, databaseName, username, password)
    sum = 0
    #ISOTIMEFORMAT = '%Y-%m-%d %H:%M:00'
    #time = datetime.datetime.today()
    #timeStrNew = time.strftime(ISOTIMEFORMAT)
    #timeStrOld = (time - datetime.timedelta(minutes=5)).strftime(ISOTIMEFORMAT)
    revenueTableName = "revenue_record"
    accountTableName = "account"
    RevenueRes = conn.query("SELECT `money`,`out_order_id`,`data_version` FROM `"+revenueTableName+"` where `status`=0 and `to_user_id`=0" )
    for data in RevenueRes:
        sum = sum + data["money"]
    i = 0
    while (i <= 10):
        companyData = conn.query("SELECT `data_version` FROM `%s` WHERE `user_id`=%s" %(accountTableName,COMPANYUSERID))
        companyAccount = companyData[0]
        companyDataVersion = companyAccount["data_version"]
        try:
            conn.begin()
            res = conn.execute_rowcount("UPDATE account SET `balance`=`balance`+%s,`data_version`=`data_version`+1 WHERE `data_version`=%s and `user_id`=0" %(sum,companyDataVersion))
            if res == 1:
                for data in RevenueRes: 
                    outOrderId = data["out_order_id"]
                    revenueDataVersion = data["data_version"]
                    conn.execute("UPDATE %s SET `status`=1 WHERE `out_order_id`='%s' and `data_version`=%s" %(revenueTableName,outOrderId,revenueDataVersion))
                conn.commit()
            break
            i = i + 1
        except:  
            conn.rollback()
