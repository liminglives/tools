# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
import random
import json
import logging


class TutorialSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class IPPOOLS(HttpProxyMiddleware):

    def __init__(self,ip=''):

        '''初始化'''

        self.ip=ip
        self.load_ip_list("iplist.dat")

    def process_request(self, request, spider):


        ip=random.choice(self.ip_pools)

        logging.info('====== current ip: '+ip['ip'])

        try:

            request.meta["proxy"]="http://"+ip['ip']

        except Exception,e:

            print e

            pass

    def load_ip_list(self, ip_list_file):
        self.ip_pools = []
        for line in open(ip_list_file, "r"):
            iplist = json.loads(line.strip())
            for ip in iplist:
                t = {}
                t["ip"] = ip["i"]+":"+ip["p"]
                self.ip_pools.append(t) 


    ip_pools=[

        #{'ip': '171.92.2.147:9000'},
        #{'ip':'183.154.212.114:9000'},
        #{'ip':'121.232.144.246:9000'},
        #{'ip':'121.232.145.159:9000'},
        #{'ip':'60.178.171.132:8081'},
        #{'ip':'221.237.154.58:9797'},
        #{'ip':'121.232.144.210:9000'},
        #{'ip':'210.83.201.51:80'},
        #{'ip':'49.140.65.25:8998'},
        #{'ip':'103.235.243.76:8118'},

    ]
