#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import logging
import requests
import json
import random
import time
import threading
import os

logger = logging.getLogger(__name__)

class ProxyPool(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.proxy_dict = {}
        self.invalid_proxy_dict = {}
        self.proxy_list = []
        self.proxy_index = 0
        self.fetching = False
        self.update_interval = 15
        self.running_flag = True
        #self.load()

    def get_html(self, url):
        request = urllib2.Request(url)
        request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36")
        html = urllib2.urlopen(request)
        return html.read()

    def get_soup(self, url):
        soup = BeautifulSoup(self.get_html(url), "lxml")
        return soup

    def fetch_kxdaili(self, page):
        """
        从www.kxdaili.com抓取免费代理
        """
        proxyes = []
        try:
            url = "http://www.kxdaili.com/dailiip/1/%d.html" % page
            soup = self.get_soup(url)
            table_tag = soup.find("table", attrs={"class": "segment"})
            trs = table_tag.tbody.find_all("tr")
            for tr in trs:
                tds = tr.find_all("td")
                ip = tds[0].text
                port = tds[1].text
                latency = tds[4].text.split(" ")[0]
                if float(latency) < 0.5: # 输出延迟小于0.5秒的代理
                    proxy = "%s:%s" % (ip, port)
                    proxyes.append(proxy)
        except:
            logger.warning("fail to fetch from kxdaili")
        return proxyes

    def img2port(self, img_url):
        """
        mimvp.com的端口号用图片来显示, 本函数将图片url转为端口, 目前的临时性方法并不准确
        """
        code = img_url.split("=")[-1]
        if code.find("AO0OO0O")>0:
            return 80
        else:
            return None

    def fetch_mimvp_fee(self):
        proxyes = []
        try:
            print 'aaaaaaaaaaaaa'
            url = 'https://proxy.mimvp.com/api/fetch.php?orderid=860170926164026729&num=100&http_type=2&result_fields=1,2'
            res = requests.get(url = url, verify = False)
            print 'mimvp fee status', res.status_code
            if int(res.status_code) == 200 and res.text.find('ERROR') == -1:
                arr = res.text.split('\n')
                for item in arr:
                    item = item.strip()
                    a = item.split(',')
                    if len(a) == 2:
                        if a[1].find('HTTPS') != -1:
                            proxyes.append(a[0].strip())
                    elif len(a) == 1:
                        proxyes.append(a[0])
        except Exception, e:
            logger.warning('fail to fetch from mimvp fee ' + str(e))

        return proxyes


    def fetch_mimvp(self):
        """
        从http://proxy.mimvp.com/free.php抓免费代理
        """
        proxyes = []
        try:
            url = "http://proxy.mimvp.com/free.php?proxy=in_hp"
            soup = self.get_soup(url)
            table = soup.find("div", attrs={"id": "list"}).table
            tds = table.tbody.find_all("td")
            for i in range(0, len(tds), 10):
                id = tds[i].text
                ip = tds[i+1].text
                port = img2port(tds[i+2].img["src"])
                response_time = tds[i+7]["title"][:-1]
                transport_time = tds[i+8]["title"][:-1]
                if port is not None and float(response_time) < 1 :
                    proxy = "%s:%s" % (ip, port)
                    proxyes.append(proxy)
        except:
            logger.warning("fail to fetch from mimvp")
        return proxyes

    def fetch_xici(self):
        """
        http://www.xicidaili.com/nn/
        """
        proxyes = []
        try:
            url = "http://www.xicidaili.com/nn/"
            soup = self.get_soup(url)
            table = soup.find("table", attrs={"id": "ip_list"})
            trs = table.find_all("tr")
            for i in range(1, len(trs)):
                tr = trs[i]
                tds = tr.find_all("td")
                ip = tds[1].text
                port = tds[2].text
                speed = tds[6].div["title"][:-1]
                latency = tds[7].div["title"][:-1]
                if float(speed) < 3 and float(latency) < 1:
                    proxyes.append("%s:%s" % (ip, port))
        except:
            logger.warning("fail to fetch from xici")
        return proxyes

    def fecth_goubanjia_fee(self):
        proxyes = []
        try:
            order = '1111'
            url = "http://dynamic.goubanjia.com/dynamic/get/" + order + ".html"
            res = requests.get(url = url)
            if int(res.status_code) == 200:
                arr = res.text.split('\n')
                for ip in arr:
                    ip = ip.strip()
                    if len(ip) > 8:
                        proxyes.append(ip)
        except:
            logger.warning('falled to fetch proxy from goubanjia fee')

        return proxyes

    def fetch_xici_fee(self):
        proxyes = []
        try:
            url = 'http://vtp.daxiangdaili.com/ip/?tid=559394621801753&num=1000&protocol=https&filter=on&longlife=20'
            res = requests.get(url = url)
            if int(res.status_code) == 200 and res.text.find('ERROR') == -1:
                arr = res.text.split('\n')
                for ip in arr:
                    ip = ip.strip()
                    if len(ip) > 8:
                        proxyes.append(ip)
        except:
            logger.warning('fail to fetch from xici fee')

        return proxyes

    def fetch_xdaili_fee(self):
        proxyes = []
        try:
            #url = 'http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD20179268842LI0gdt/d0c3c34bf83211e6942200163e1a31c0?returnType=2'
            #url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=199f073d3f0246698cd2a4e3a9fdfe95&orderno=YZ20179267433YBhYdh&returnType=2&count=15'
            #url = 'http://api.xdaili.cn/xdaili-api//newExclusive/getIp?spiderId=199f073d3f0246698cd2a4e3a9fdfe95&orderno=MF20179297691biR1yS&returnType=2&count=1&machineArea='
            #url = 'http://api.xdaili.cn/xdaili-api//privateProxy/applyStaticProxy?spiderId=199f073d3f0246698cd2a4e3a9fdfe95&returnType=2&count=1'
            url = 'http://api.xdaili.cn/xdaili-api//privateProxy/applyStaticProxy?spiderId=199f073d3f0246698cd2a4e3a9fdfe95&returnType=2&count=1'
            res = requests.get(url = url)
            if int(res.status_code) == 200:
                print res.text
                j = json.loads(res.text)
                if int(j['ERRORCODE']) == 0:
                    if isinstance(j['RESULT'], list):
                        for i in j['RESULT']:
                            ip = i['ip']
                            port = i['port']
                            proxyes.append('%s:%s' % (ip, port))
                    else:
                        ip = j['RESULT']['wanIp']
                        port = j['RESULT']['proxyport']
                        proxyes.append('%s:%s' % (ip, port))
        except:
            logger.warning('failed to fetch from xdaili fee')


        return proxyes

    def fetch_ip181(self):
        """
        http://www.ip181.com/
        """
        proxyes = []
        try:
            url = "http://www.ip181.com/"
            soup = self.get_soup(url)
            table = soup.find("table")
            trs = table.find_all("tr")
            for i in range(1, len(trs)):
                tds = trs[i].find_all("td")
                ip = tds[0].text
                port = tds[1].text
                latency = tds[4].text[:-2]
                if float(latency) < 1:
                    proxyes.append("%s:%s" % (ip, port))
        except Exception as e:
            logger.warning("fail to fetch from ip181: %s" % e)
        return proxyes

    def fetch_xudailifree(self):
        proxyes = []
        try:
            url = "http://www.xdaili.cn/freeproxy"
            soup = self.get_soup(url)
            table = soup.find("table")
            trs = table.find_all("tr")
            for i in range(1, len(trs)):
                tds = trs[i].find_all("td")
                ip = tds[0].text
                port = tds[1].text
                latency = tds[5].text
                if float(latency) < 3:
                    proxyes.append("%s:%s" % (ip, port))
        except Exception as e:
            logger.warning("fail to fetch from xdaili free: %s" % e)
        return proxyes


    def fetch_httpdaili(self):
        """
        http://www.httpdaili.com/mfdl/
        更新比较频繁
        """
        proxyes = []
        try:
            url = "http://www.httpdaili.com/mfdl/"
            soup = self.get_soup(url)
            table = soup.find("div", attrs={"kb-item-wrap11"}).table
            trs = table.find_all("tr")
            for i in range(1, len(trs)):
                try:
                    tds = trs[i].find_all("td")
                    ip = tds[0].text
                    port = tds[1].text
                    type = tds[2].text
                    if type == u"匿名":
                        proxyes.append("%s:%s" % (ip, port))
                except:
                    pass
        except Exception as e:
            logger.warning("fail to fetch from httpdaili: %s" % e)
        return proxyes

    def fetch_66ip(self):
        """
        http://www.66ip.cn/
        每次打开此链接都能得到一批代理, 速度不保证
        """
        proxyes = []
        try:
            # 修改getnum大小可以一次获取不同数量的代理
            url = "http://www.66ip.cn/nmtq.php?getnum=10&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip"
            content = self.get_html(url)
            urls = content.split("</script>")[-1].split("<br />")
            for u in urls:
                if u.strip():
                    proxyes.append(u.strip())
        except Exception as e:
            logger.warning("fail to fetch from httpdaili: %s" % e)
        return proxyes



    def check(self, proxy):
        if not proxy:
            return False
        if proxy in self.proxy_dict:
            return True
        import urllib2
        #url = "http://www.baidu.com/js/bdsug.js?v=1.0.3.0"
        url = 'https://www.tmall.com/'
        #url = 'http://www.tmall.com/'
        proxy_handler = urllib2.ProxyHandler({'https': "https://" + proxy})
        opener = urllib2.build_opener(proxy_handler,urllib2.HTTPHandler)
        try:
            response = opener.open(url,timeout=1)
            return response.code == 200 and response.url == url
        except Exception:
            return False

    def next_valid_proxy_index(self, protocol='https'):
        cur_index = self.proxy_index
        self.proxy_index += 1
        found = False
        while cur_index != self.proxy_index:
            self.proxy_index = self.proxy_index % len(self.proxy_list)
            if self.proxy_list[self.proxy_index]['valid']:
                found = True
                break
        return (found, self.proxy_index, self.proxy_list[self._proxy_index])

    def get_proxy(self, protocol='https'):
        retry = 0
        while len(self.proxy_dict) == 0:
            self.update_proxy()
            if retry > 1:
                return None
            retry += 1
            time.sleep(6)

        key = random.choice(self.proxy_dict.keys())

        proxy = self.proxy_dict.get(key)
        proxy['count'] += 1
        proxy['time'] = int(time.time())
        return proxy[protocol]

    def set_proxy_invalid(self, proxy):
        idx = proxy.find("//")
        if idx != -1:
            proxy = proxy[idx + len('//'):]
        if proxy in self.proxy_dict:
            v = self.proxy_dict.pop(proxy)
            self.invalid_proxy_dict[proxy] = v

    def update_proxy(self):
        proxy_list = self.fetch_all()
        if not proxy_list:
            return
        for p in proxy_list:
            self.proxy_list.append({'http':'http://'+p, 'https':'https://'+p, 'count':0, 'valid':True, 'time': 0})
            if p not in self.proxy_dict:
                self.proxy_dict[p] = {'http':'http://'+p, 'https':'https://'+p, 'count':0, 'time': 0}
            if p in self.invalid_proxy_dict:
                print p, 'has been set invalid'

    def quit(self):
        self.running_flag = False

    def run(self):
        last_update_time = 0
        logger.info('ProxyPool start')
        while self.running_flag:
            now = time.time()
            if now - last_update_time >= self.update_interval:
                try:
                    last_update_time = now
                    self.update_proxy()
                except Exception, e:
                    logger.error('Exception:' + str(e))
            time.sleep(1)
        logger.info('ProxyPool end')
        self.dump()

    def fetch_all(self, endpage=2):
        if self.fetching:
            return
        self.fetching = True
        proxyes = []
        #for i in range(1, endpage):
        #    proxyes += self.fetch_kxdaili(i)
        #proxyes += self.fetch_mimvp()
        #proxyes += self.fetch_xici()
        #proxyes += self.fetch_ip181()
        #proxyes += self.fetch_httpdaili()
        #proxyes += self.fetch_66ip()
        #proxyes += self.fetch_xudailifree()
        proxyes += self.fetch_xdaili_fee()

        #proxyes += self.fetch_xici_fee()
        #proxyes += self.fetch_mimvp_fee()
        valid_proxyes = []
        logger.info("checking proxyes validation")
        for p in proxyes:
            if self.check(p):
                valid_proxyes.append(p)
                print 'check ok', p
        self.fetching = False
        return valid_proxyes

    def dump(self):
        with open('proxy.data', 'w') as f:
            f.write(json.dumps(self.proxy_dict))

    def load(self):
        path = 'proxy.data'
        if os.path.exists(path):
            with open(path) as f:
                data = f.read()
                self.proxy_dict = json.loads(data)

if __name__ == '__main__':
    import sys
    root_logger = logging.getLogger("")
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(name)-8s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    pool = ProxyPool()
    pool.update_proxy()
    pool.setDaemon(True)
    pool.start()
    start = time.time()
    while True:
        now = time.time()
        if now - start > 60:
            break
        print pool.get_proxy()
        time.sleep(2)
    pool.quit()
    pool.dump()
