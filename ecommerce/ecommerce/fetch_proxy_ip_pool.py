#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import logging
import requests
import json

logger = logging.getLogger(__name__)

def get_html(url):
    request = urllib2.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36")
    html = urllib2.urlopen(request)
    return html.read()

def get_soup(url):
    soup = BeautifulSoup(get_html(url), "lxml")
    return soup

def fetch_kxdaili(page):
    """
    从www.kxdaili.com抓取免费代理
    """
    proxyes = []
    try:
        url = "http://www.kxdaili.com/dailiip/1/%d.html" % page
        soup = get_soup(url)
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

def img2port(img_url):
    """
    mimvp.com的端口号用图片来显示, 本函数将图片url转为端口, 目前的临时性方法并不准确
    """
    code = img_url.split("=")[-1]
    if code.find("AO0OO0O")>0:
        return 80
    else:
        return None

def fetch_mimvp_fee():
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


def fetch_mimvp():
    """
    从http://proxy.mimvp.com/free.php抓免费代理
    """
    proxyes = []
    try:
        url = "http://proxy.mimvp.com/free.php?proxy=in_hp"
        soup = get_soup(url)
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

def fetch_xici():
    """
    http://www.xicidaili.com/nn/
    """
    proxyes = []
    try:
        url = "http://www.xicidaili.com/nn/"
        soup = get_soup(url)
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

def fetch_xici_fee():
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

def fetch_xdaili_fee():
    proxyes = []
    try:
        url = 'http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD20179268842LI0gdt/d0c3c34bf83211e6942200163e1a31c0?returnType=2'
        #url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=199f073d3f0246698cd2a4e3a9fdfe95&orderno=YZ20179267433YBhYdh&returnType=2&count=15'
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

def fetch_ip181():
    """
    http://www.ip181.com/
    """
    proxyes = []
    try:
        url = "http://www.ip181.com/"
        soup = get_soup(url)
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

def fetch_xudailifree():
    """
    http://www.ip181.com/
    """
    proxyes = []
    try:
        url = "http://www.xdaili.cn/freeproxy"
        soup = get_soup(url)
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


def fetch_httpdaili():
    """
    http://www.httpdaili.com/mfdl/
    更新比较频繁
    """
    proxyes = []
    try:
        url = "http://www.httpdaili.com/mfdl/"
        soup = get_soup(url)
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

def fetch_66ip():
    """
    http://www.66ip.cn/
    每次打开此链接都能得到一批代理, 速度不保证
    """
    proxyes = []
    try:
        # 修改getnum大小可以一次获取不同数量的代理
        url = "http://www.66ip.cn/nmtq.php?getnum=10&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip"
        content = get_html(url)
        urls = content.split("</script>")[-1].split("<br />")
        for u in urls:
            if u.strip():
                proxyes.append(u.strip())
    except Exception as e:
        logger.warning("fail to fetch from httpdaili: %s" % e)
    return proxyes



def check(proxy):
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
        print 'failed', proxy
        return False

def fetch_all(endpage=2):
    proxyes = []
    #for i in range(1, endpage):
    #    proxyes += fetch_kxdaili(i)
    #proxyes += fetch_mimvp()
    #proxyes += fetch_xici()
    #proxyes += fetch_ip181()
    #proxyes += fetch_httpdaili()
    #proxyes += fetch_66ip()
    #proxyes += fetch_xudailifree()
    proxyes += fetch_xdaili_fee()
    #proxyes += fetch_xici_fee()
    #proxyes += fetch_mimvp_fee()
    valid_proxyes = []
    logger.info("checking proxyes validation")
    for p in proxyes:
        if check(p):
            valid_proxyes.append(p)
            print 'check ok', p
    return valid_proxyes

if __name__ == '__main__':
    import sys
    root_logger = logging.getLogger("")
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(name)-8s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    proxyes = fetch_all()
    #print check("202.29.238.242:3128")
    for p in proxyes:
        print p
