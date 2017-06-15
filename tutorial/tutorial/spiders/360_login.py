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

class Login360Spider(Spider):

    name = "360_login"
    start_urls = ['https://www.so.com/']

    cookieFile = None
    cookie_jar = None
    userFile = None

    def parse(self, response):
        self.login()

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

    

