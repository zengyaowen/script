#!/usr/bin/env python
# encoding: utf-8

import common.db
import sys
from common.config import Config
from common.sendEmail import *


EMAIL_MESSAGE = ""


#校验各个账户以及其对应的日志
def checkData(todayData, yesterdayData, records):
    global EMAIL_MESSAGE
    #只校验非公司账号的一般用户账号
    keys = list(set(todayData.keys() + yesterdayData.keys())).remove(1)
    for key in keys:
        yesterdaySnapShot = yesterdayData.get(key)
        todaySnapShot = todayData.get(key)
        if yesterdaySnapShot is not None or todaySnapShot is not None:
            if cmp(yesterdaySnapShot, todaySnapShot) == 0:
                EMAIL_MESSAGE = EMAIL_MESSAGE + ("userId:" + str(key) + " has not changed during yesterday\n")
                continue
        EMAIL_MESSAGE = EMAIL_MESSAGE + ("userId:" + str(key) + " has been changed during yesterday\n")
        yesterdayBalance = 0 if (yesterdaySnapShot is None) else yesterdaySnapShot['balance']
        todayBalance = 0 if todaySnapShot is None else todaySnapShot['balance']
        if records is None:
            EMAIL_MESSAGE = EMAIL_MESSAGE + ("userId:" + str(key) + " is invalid because the data has been changed but there is no record\n")
            continue
        if not key in records:
            EMAIL_MESSAGE = EMAIL_MESSAGE +("userId:" + str(key) + " is invalid because the data has been changed but there is no record\n")
            continue
        recordList = records[key]
        for record in recordList:
            if record['user_id'] == key:
                yesterdayBalance = yesterdayBalance - record['money']
            if record['to_user_id'] == key:
                yesterdayBalance = yesterdayBalance + record['money']
        if yesterdayBalance == todaySnapShot['balance']:
            EMAIL_MESSAGE = EMAIL_MESSAGE + ("userId:" + str(key) + " valid and pass\n")
            continue
        else:
            EMAIL_MESSAGE = EMAIL_MESSAGE + ("userId:" + str(key) + " is invalid\n")
            EMAIL_MESSAGE = EMAIL_MESSAGE + (records[key]) + "\n"


#检查记录
def checkRecord(todayData, yesterdayData, records):
    keys = list(set(todayData.keys() + yesterdayData.keys()))
    recordKeys = records.keys()
    for key in recordKeys:
        if key in keys:
            continue


def initDB(ip, dbname, name, pwd):
    return common.db.Connection(ip, dbname, name, pwd, True, 'utf8mb4')


def valildRecord(startTime, endTime, recordList):
    result = []
    for record in recordList:
        if startTime and record['update_time'] < startTime:
            continue
        if endTime and record['update_time'] > endTime:
            continue
        else:
            result.append(record)
    return result


def recordList2Map(recordsIter):
    records = dict()
    for record in recordsIter:
        if record['user_id'] in records:
            records[record['user_id']].append(record)
        else:
            valueList = [record]
            records[record['user_id']] = valueList
        if record['to_user_id'] in records:
            records[record['to_user_id']].append(record)
        else:
            valueList = [record]
            records[record['to_user_id']] = valueList
    return records


def getRecord(YAD, TAD, recordsIter):
    records = dict()
    records = recordList2Map(recordsIter)
    keys = set(YAD.keys() + TAD.keys())
    for key in keys:
        startTime = 0
        endTime = 0
        recordList = records.get(key)
        startRecordId = YAD.get(key)['trade_id'] if key in YAD else -1
        endRecordId = TAD.get(key)['trade_id'] if key in TAD else -1
        for record in recordList:
            if startRecordId is not None and record['id'] == startRecordId:
                startTime = record['update_time']
            if endRecordId is not None and record['id'] == endRecordId:
                endTime = record['update_time']
        resultList = valildRecord(startTime, endTime, recordList)
        records[key] = resultList
    return records


def checkCompanyData(YAD, TAD, recordList, conn):
    global EMAIL_MESSAGE    
    unprocessRecords = conn.query("SELECT * FROM revenue_record where status = 0")
    oldMoney = YAD['1']['balance'] if "1" in YAD else 0
    todayMoney = TAD['1']['balance'] if "1" in TAD else 0
    for record in recordList:
        if record['user_id'] == 1:
            oldMoney = oldMoney - record['money']
        elif record['to_user_id'] == 1:
            oldMoney = oldMoney + record['money']
    for unprocessRecord in unprocessRecords:
        if unprocessRecord['user_id'] == 1:
            oldMoney = oldMoney - unprocessRecord['money']
        elif unprocessRecord['to_user_id'] == 1:
            oldMoney = oldMoney + unprocessRecord['money']
    if oldMoney == todayMoney:
        EMAIL_MESSAGE = EMAIL_MESSAGE + "the company record is valid\n"
    else:
        EMAIL_MESSAGE = EMAIL_MESSAGE + "the company record is invalid\n"
        EMAIL_MESSAGE = EMAIL_MESSAGE + "yesterday account : " + YAD
        EMAIL_MESSAGE = EMAIL_MESSAGE + "today account : " + TAD
        EMAIL_MESSAGE = EMAIL_MESSAGE + "the relative record as follow"
        EMAIL_MESSAGE = EMAIL_MESSAGE + ".".join(recordList) + "\n" + ",".join(unprocessRecords)


def sendEmail(receivers):
    global EMAIL_MESSAGE
    email = emailSender()
    fromPerson = "check bill"
    Subject = "check bill"
    content = email.buildMessage(fromPerson, "", Subject, EMAIL_MESSAGE)
    email.sendEmail(receivers, content)

if __name__ == "__main__":
    env = sys.argv[1]
    config = Config(env)
    ip = config.getValue("db", "ip")
    username = config.getValue("db", "username")
    databaseName = config.getValue("db", "database")
    password = config.getValue("db", "password")
    conn = initDB(ip, databaseName, username, password)
    ISOTIMEFORMAT = '%Y-%m-%d'
    #todayTimeStr = datetime.date.today().strftime(ISOTIMEFORMAT)
    #yesterdayTimeStr = (datetime.date.today()+datetime.timedelta(-1)).strftime(ISOTIMEFORMAT)
    #tomorrorTimeStr = (datetime.date.today()+datetime.timedelta(1)).strftime(ISOTIMEFORMAT)
    yesterdayTimeStr = "2015-11-27"
    tomorrorTimeStr = "2015-11-29"
    todayTimeStr = "2015-11-28"
    todayTableName = "account"+todayTimeStr
    yesterdayTableName = "account" + yesterdayTimeStr
    todayAccountDataIter = conn.iter("SELECT * FROM `"+todayTableName+"`" )
    yesterdayAccountDataIter = conn.iter("SELECT * FROM `" + yesterdayTableName+"`")
    recordsIter = conn.iter("SELECT * FROM trade_record where update_time<\'" + tomorrorTimeStr +"\' AND update_time > \'" + yesterdayTimeStr+"\'")
    YAD = dict()
    TAD = dict()
    for data in yesterdayAccountDataIter:
        YAD[data['user_id']] = data
    for data in todayAccountDataIter:
        TAD[data['user_id']] = data
    records = getRecord(YAD, TAD, recordsIter)
    checkData(TAD, YAD, records)
    #checkRecord(TAD, YAD, records)
    checkCompanyData(YAD, TAD, records["1"])
    print(EMAIL_MESSAGE)
    sendEmail(['zengyaowen@imxiaomai.com', 'qiaoyang@imxiaomai.com'])
