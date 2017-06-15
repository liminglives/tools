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
        

    def login__(self):
        yield self.login_().next()

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



    def loginInit(self):
        
        self.userFile = './360_user.dat'
        self.cookieFile = './360_cookie.dat' 
        
        open(self.userFile, 'w').close()
        
        open(self.cookieFile, 'w').close()

        self.cookie_jar  = cookielib.LWPCookieJar(self.cookieFile)
        print "login init"
        try:
            self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
        except Exception:
            self.cookie_jar.save(self.cookieFile, ignore_discard=True, ignore_expires=True)
        
        cookie_support = urllib2.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)

    def replace_cookiefile_domain(self):
        tmp = self.cookieFile+".tmp"
        w = open(tmp, "wb")
        with open(self.cookieFile, "r") as f:
            for line in f:
                w.write(line.replace("360.cn", "so.com"))

        w.close()
        os.remove(self.cookieFile)
        os.rename(tmp, self.cookieFile)


    def getToken(self, username):
        '''根据用户名等信息获得登陆的token值
            
            username String 用户名
            return 返回Token 值
        '''
        login = {
            'callback' : 'QiUserJsonP1377767974691',
            'func' : 'test',
            'm' : 'getToken',
            'o' : 'sso',
            'rand' : str(random.random()),
            'userName' : username
        }

        url = "https://login.360.cn/?"
        queryString = urllib.urlencode(login)
        url += queryString
        print "url:", url
        result = urllib2.urlopen(url).read()
        print "result:", result
        result = result.strip(' ')
        result = json.loads(result[5:-1])
        token = ''
        if int(result['errno']) == 0:
            print 'getToken Success'
            token = result['token']
            self.cookie_jar.save(self.cookieFile, ignore_discard=True, ignore_expires=True)
        else:
            print 'getToken Failed, Errno:' + str(result['errno'])
            sys.exit()
        return token


    def doLogin(self, username, password, token):
        '''开始执行登陆操作
            
            username String 用户名
            password String 密码
            token String 根据getToken获得
        '''
        login = {
            'callback' : 'QiUserJsonP1377767974692',
            'captFlag' : '',
            'from' : 'pcw_so',
            'func' : 'test',
            'isKeepAlive' : '0',
            'm' : 'login',
            'o' : 'sso',
            'password' : self.pwdHash(password),
            'pwdmethod' : '1',
            'r' : str((long)(time.time()*100)),
            'rtype' : 'data',
            'token' : token,
            'userName' : username
        }
        url = "https://login.360.cn/?"
        queryString = urllib.urlencode(login)
        url += queryString
        result = urllib2.urlopen(url).read()
        result = result.replace("\n", '').strip(' ')
        result = json.loads(result[5:-1])
        userinfo = {}
        if int(result['errno']) == 0:
            print 'Login Success'
            userinfo = result['userinfo']
            open(self.userFile, 'w').write(json.dumps(userinfo))
            self.cookie_jar.save(self.cookieFile, ignore_discard=True, ignore_expires=True)
            self.replace_cookiefile_domain()
        else:
            print 'Login Failed, please check your password in cli.py or main.py, Errno:' + str(result['errno'])
            sys.exit()
        return userinfo


    def check(self):
        '''验证是否登录
            
            return True 已登录 False 未登录
        '''
        url = 'https://www.so.com/?src=so.com'
        result = urllib2.urlopen(url).read()
        with open("index.html", "wb") as f:
            f.write(result)

        #regx = "web : '([^']*)'"
        regx = 'class="uname"'
        uname = re.findall(regx, result)
        if len(uname) and uname[0] != '' > 0:
            print "Get Server Success, Server Address:" + uname[0]
            return True
        else:
            print "Logining!"
            return False

    def login(self):
        account = ["18818213619:liming012389"]
        for line in account:
        #for line in open("360_account.conf"):
            username, password = line.strip().split(":")
            self.loginInit()
            if self.run(username, password):
                break

    def run(self, username, password):
        '''开始执行登陆流程
            
            username String 用户名
            password String 密码
        '''
        userinfo = None
        if self.check():
            print 'Login Success!'
            userinfo = open(self.userFile).read()
            userinfo = json.loads(userinfo)
            return True
        else:
            # 获取token
            token = self.getToken(username)
            # 登陆
            userinfo = self.doLogin(username, password, token)
            
            return self.check()
        #return userinfo


    def pwdHash(self, password):
        '''md5操作函数用于密码加密

            password String 需要加密的密码
            return 加密后的密码
        '''
        md5 = hashlib.md5()
        md5.update(password)
        return md5.hexdigest()



if __name__ == '__main__':
    login = Login360Spider()
    userinfo = login.run('18818213619', 'liming012389')
    print userinfo

    

