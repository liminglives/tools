# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import logging
import hashlib
import time
from proxy_pool import ProxyPool
import logging
from scrapy.xlib.pydispatch import dispatcher

from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError

#class ProxyMiddleware(object):
#    def __init__(self, settings):
#        orderno = ''
#        secret = ''
#        ts = str(int(time.time()))
#        s = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + ts
#        md5_string = hashlib.md5(s).hexdigest()
#        self.sign = md5_string.upper()
#        self.auth = "sign=" + self.sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + ts
#
#    def process_request(self, request, spider):
#        logging.info('77777777777777777 proxy')
#        request.meta['proxy'] = 'https://117.78.37.198:8000'
#        request.headers['Proxy-Authorization'] = self.auth

class ProxyPoolMiddleware(object):
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)
    def __init__(self, settings):
        self.pool = ProxyPool()
        self.pool.setDaemon(True)
        self.pool.start()
        dispatcher.connect(self.close, signals.engine_stopped)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def close(self):
        self.pool.quit()

    def set_proxy(self, request):
        proxy = self.pool.get_proxy()
        if proxy:
            request.meta['proxy'] = proxy
        elif 'proxy' in request.meta.keys():
            del request.meta['proxy']

    def invalid_proxy(self, request):
        if 'proxy' not in request.meta.keys():
            return
        proxy = request.meta['proxy']
        self.pool.set_proxy_invalid(proxy)

    def process_request(self, request, spider):
        request.meta["dont_redirect"] = True
        if 'change_proxy' in request.meta.keys() and request.meta['change_proxy']:
            logging.info('==== change proxy by request: %s', request)
            self.invalid_proxy(request)
            request.meta['change_proxy'] = False

        self.set_proxy(request)

    def process_response(self, request, response, spider):
        if "proxy" in request.meta.keys():
            logging.info("response: %s %s %s %s,  header:%s" % (str(request.meta["proxy"]), str(response.status), request.url, response.url, str(response.headers)))
        else:
            logging.info("response: None %s %s %s, headers:" % (str(response.status), request.url, response.url, str(response.headers)))

        if response.status != 200: #and response.status != 302:
            self.invalid_proxy(request)
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response

    def process_exception(self, request, exception, spider):
        if "proxy" in request.meta.keys():
            logging.info("exception: %s %s %s" % (request.meta["proxy"], request.url, exception))
        else:
            logging.info("exception: None %s %s" % (request.url, exception))

        if isinstance(exception, self.DONT_RETRY_ERRORS):
            self.invalid_proxy(request)
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request


#class EcommerceSpiderMiddleware(object):
#    # Not all methods need to be defined. If a method is not defined,
#    # scrapy acts as if the spider middleware does not modify the
#    # passed objects.
#
#    @classmethod
#    def from_crawler(cls, crawler):
#        # This method is used by Scrapy to create your spiders.
#        s = cls()
#        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#        return s
#
#    def process_spider_input(self, response, spider):
#        # Called for each response that goes through the spider
#        # middleware and into the spider.
#
#        # Should return None or raise an exception.
#        return None
#
#    def process_spider_output(self, response, result, spider):
#        # Called with the results returned from the Spider, after
#        # it has processed the response.
#
#        # Must return an iterable of Request, dict or Item objects.
#        for i in result:
#            yield i
#
#    def process_spider_exception(self, response, exception, spider):
#        # Called when a spider or process_spider_input() method
#        # (from other spider middleware) raises an exception.
#
#        # Should return either None or an iterable of Response, dict
#        # or Item objects.
#        pass
#
#    def process_start_requests(self, start_requests, spider):
#        # Called with the start requests of the spider, and works
#        # similarly to the process_spider_output() method, except
#        # that it doesn’t have a response associated.
#
#        # Must return only requests (not items).
#        for r in start_requests:
#            yield r
#
#    def spider_opened(self, spider):
#        spider.logger.info('Spider opened: %s' % spider.name)
