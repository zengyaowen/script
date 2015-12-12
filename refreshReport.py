#!/usr/bin/env python
# encoding:utf-8

import common.db
import sys
from common.config import Config
from common.httpClinet import HttpClient
import datetime

def initDB(ip, dbname, name, pwd):
    return common.db.Connection(ip, dbname, name, pwd, True, 'utf8mb4')


def getUnprocessReportList(conn):
    timeStamp = (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime("%Y-%m%d %H:%M:%S")
    return conn.query("SELECT * FROM trade_record WHERE status != 2 AND create_time > \'" + timeStamp + "\'")

#处理订单状态为非支付完成的订单
#重新确认该订单状态
def processRecord(recordList, conn):
    for record in recordList:
        if record:
            recordId = record['id']
            url = config.getValue("checkRecord", "url") + "?&orderId=" + str(recordId)
            print url
            result = HttpClient.get(url)
            print result


if __name__ == "__main__":
    env = sys.argv[1]
    config = Config(env)
    ip = config.getValue("db", "ip")
    username = config.getValue("db", "username")
    databaseName = config.getValue("db", "database")
    password = config.getValue("db", "password")
    conn = initDB(ip, databaseName, username, password)
    unprocessRecordList = getUnprocessReportList(conn)
    processRecord(unprocessRecordList, conn)
