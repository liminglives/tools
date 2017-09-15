# -*- coding: utf8 -*-

import sys
import urllib
import urllib2
import cookielib
import time
import random
import hashlib
import json
import re
import os
from scrapy.spiders import Spider
from scrapy.http import Request
import logging

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='360_login_spider.log',
                filemode='a') #default 'a', if set 'w', the log file will be rewrite every runtime.

class Login360Spider(Spider):

    name = "360_login2"
    start_urls = ['https://www.so.com/']

    cookieFile = "360_cookie2.dat"
    cookie_jar = None
    userFile = None
    username = ""
    password = ""

    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, sdch",
        "Accept-Language":"zh-CN,zh;q=0.8",
        "Cache-Control":"max-age=0",
        "Connection":"keep-alive",
        "Host":"www.so.com",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    def parse(self, response):
        yield self.login_()

    def login_(self):
        account = ["18818213619:liming012389"]
        for line in account:
        #for line in open("360_account.conf"):
            self._username, self._password = line.strip().split(":")
            
            #yield self.get_token()
            login = {
                'callback' : 'QiUserJsonP1377767974691',
                'func' : 'test',
                'm' : 'getToken',
                'o' : 'sso',
                'rand' : str(random.random()),
                'userName' : self._username
            }

            url = "https://login.360.cn/?"
            query = urllib.urlencode(login)
            url += query
            logging.info("url:"+url)
            self.headers["Host"] = "login.360.cn"
            request = Request(url, headers=self.headers,callback=self.parse_get_token_result)

            return request

    def get_token(self):
        login = {
            'callback' : 'QiUserJsonP1377767974691',
            'func' : 'test',
            'm' : 'getToken',
            'o' : 'sso',
            'rand' : str(random.random()),
            'userName' : self._username
        }

        url = "https://login.360.cn/?"
        query = urllib.urlencode(login)
        url += query
        print "url:", url
        logging.info("url:"+url)
        self.headers["Host"] = "login.360.cn"
        request = Request(url, headers=self.headers,callback=self.parse_get_token_result)

        return request

    def parse_get_token_result(self, response):
        if response.status is not 200:
            logging.error("get token page failed status:%d" % response.status)

        result = str(response.body)
        logging.info("result:" + result)
        result = result.strip(' ')
        result = json.loads(result[5:-1])
        if int(result['errno']) == 0:
            logging.info('getToken Success')
            self._token = result['token']
            logging.info("token:%s" % self._token)
            with open(self.cookieFile, "wb") as f:
                j = json.dumps(response.headers.getlist('Set-Cookie'))
                f.write(j)
                f.write('\n')
            yield self.do_login()

        else:
            print logging.error('getToken Failed, Errno:' + str(result['errno']))

    def do_login(self):
        login = {
            'callback' : 'QiUserJsonP1377767974692',
            'captFlag' : '',
            'from' : 'pcw_so',
            'func' : 'test',
            'isKeepAlive' : '0',
            'm' : 'login',
            'o' : 'sso',
            'password' : self.pwdHash(self._password),
            'pwdmethod' : '1',
            'r' : str((long)(time.time()*100)),
            'rtype' : 'data',
            'token' : self._token,
            'userName' : self._username
        }
        url = "https://login.360.cn/?"
        query = urllib.urlencode(login)
        url += query
        logging.info("url:"+url)
        self.headers["Host"] = "login.360.cn"
        request = Request(url, headers=self.headers,callback=self.parse_do_login_result)

        return request

    def parse_do_login_result(self, response):
        if response.status is not 200:
            logging.error("do login page failed status:%d" % response.status)

        logging.info("response:" + str(response.body))
        result = response.body
        result = result.replace("\n", '').strip(' ')
        result = json.loads(result[5:-1])
        userinfo = {}
        if int(result['errno']) == 0:
            logging.info('Login Success')
            userinfo = result['userinfo']
            with open(self.cookieFile, "a") as f:
                f.write(json.dumps(response.headers.getlist('Set-Cookie')) + "\n")
                f.write(json.dumps(response.request.headers.getlist('Cookie')) + "\n")
                f.write(json.dumps(userinfo))
        else:
            logging.info('Login Failed, please check your password in cli.py or main.py, Errno:' + str(result['errno']))




    def pwdHash(self, password):
        '''md5操作函数用于密码加密

            password String 需要加密的密码
            return 加密后的密码
        '''
        md5 = hashlib.md5()
        md5.update(password)
        return md5.hexdigest()


    

