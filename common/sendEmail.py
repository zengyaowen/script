#!/usr/bin/env python
# encoding: utf-8

import smtplib


class emailSender():
    sender = 'zengyaowen@imxiaomai.com'
    password = "Fytyzyw1987"
    receivers = ['zengyaowen@imxiaomai.com']
    smtpObj = ""

    def __init__(self):
        try:
            self.smtpObj = smtplib.SMTP()
            self.smtpObj.connect('smtp.qq.com')
            self.smtpObj.login(self.sender, self.password)
            print "Successfully init email"
        except Exception:
            print "Error: unable to send email"

    def sendEmail(self, receivers, message):
        self.receivers = receivers
        self.message = message
        self.smtpObj.sendmail(self.sender, self.receivers, self.message)

    def buildMessage(self, fromPerson, toPerson, subject, content):
        messageStr = "From:" + fromPerson + "\n"
        messageStr = messageStr + "To:" + toPerson + "\n"
        messageStr = messageStr + "Subject:" + subject + "\n"
        messageStr = messageStr + "\n" + content
        return messageStr
