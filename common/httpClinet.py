#!/usr/bin/env python
# encoding:utf-8

import urllib


class HttpClient():
    @staticmethod
    def get(url):
        try:
            content = urllib.urlopen(url)
            return content.read()
        except Exception, e:
            print e
