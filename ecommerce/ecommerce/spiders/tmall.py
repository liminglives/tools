# -*- coding: utf-8 -*-

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')   

import scrapy
import logging
from ecommerce.items import EcommerceItem

class TmallSpider(scrapy.Spider):
    name = 'tmall'
    allowed_domains = ['tmall.com']
    url_host = "https://list.tmall.com"
    url_path = "/search_product.htm?sort=d&q="
    start_urls = [
        'https://list.tmall.com/search_product.htm?sort=d&q=apple',
        #'https://www.tmall.com'
    ]
    seq = 0

    hheaders = {
        #"authority":"list.tmall.com",
        #"method":"GET",
        #"path":"/search_product.htm?sort=d&q=apple",
        #"scheme":"https",
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding":"gzip, deflate, sdch, br",
        "accept-language":"zh-CN,zh;q=0.8",
        "upgrade-insecure-requests":"1",
        "Cache-control":"max-age=0",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    }

    #cookie = {"cookie2":"18d011caacea5cc233620bb4662dcfc1", "t":"917c68ce59c74e1ff951ce3d10f85173", "_tb_token_":"3e305a7773e73"}
    cookie = {'pnm_cku822': '053UW5TcyMNYQwiAiwQRHhBfEF8QXtHcklnMWc%3D%7CUm5Ockt%2FRX1BdUl0SHRMdCI%3D%7CU2xMHDJ7G2AHYg8hAS8XIgwsAl4%2FWTVSLFZ4Lng%3D%7CVGhXd1llXGhSalZiXmNfY1tjVGlLf0J6RXhHe0J7Q3pDfEB9SWcx%7CVWldfS0TMwowDi4QMB4%2BBycJXwk%3D%7CVmhIGCUFOBgkHCkXNwwxDjoaJh0gHT0JNAkpFS4TLg47AD1rPQ%3D%3D%7CV25Tbk5zU2xMcEl1VWtTaUlwJg%3D%3D', 'cookie2': '107f1cda7786efd49c936682831630a0', 'isg': 'AlVVgGIIoNYQSYTX7bpqrI_iZFHP-sEgexDXBtf6FEwbLnUgn6IZNGPsjgRj', 'res': 'scroll%3A1583*6029-client%3A1583*794-offset%3A1583*6029-screen%3A1600*900', 'sm4': '310100', 'l': 'AtbWc7Qb21jdcFYTShEr6844pofYdxqx', 't': '6144bba42e39924704079cb1fb909e3c', '_m_h5_tk': '2098407e44994fb6a22a82ef41186a3a_1497519252292', 'cna': '0FrBEXmazlsCAXbyG27/LQqQ', 'cq': 'ccp%3D1', '_m_h5_tk_enc': 'fd5bab0717d458f1425740cb70270337', '_tb_token_': 'c51bb3c61eadb', '_med': 'dw:1600&dh:900&pw:1600&ph:900&ist:0'}

    #user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Mobile Safari/537.36"

    def start_requestss(self):

        yield scrapy.Request(
            url = self.start_urls[0],
            headers = self.hheaders,
            #cookies = self.cookie,
            callback = self.parse)

    def parse(self, response):
    	logging.info(response.headers.getlist("Set-Cookie"))
    	logging.info(response.request.headers.getlist("Cookie"))
    	for brand in open("brand_list.dat", "r"):
    		brand = brand.strip()
    		path = self.url_path + brand
    		url = self.url_host + path
    		#self.headers 
    		logging.info(url)
    		yield scrapy.Request(
                url = url,
                headers = self.hheaders,
                #cookies = self.cookie,
                callback = self.tmall_parse)


    def tmall_parse(self, response):
    	logging.info("cookie=" + str(response.headers.getlist("Set-Cookie")))
    	logging.info("cookie=" + str(response.request.headers.getlist("Cookie")))
    	self.seq += 1
    	logging.info("parse===================")
    	with open("tmall%s.html" % str(self.seq), "wb") as f:
    		f.write(response.body)
        products = response.xpath('//div[@class="product  "]')
        logging.info("start parse")
        f = open("item.text", "w")
        for product in products:
        	logging.info(str(product))
        	item = EcommerceItem()
        	item["data_id"] = product.xpath('.//@data-id').extract_first()
        	item["price"] = product.xpath('.//p[@class="productPrice"]').xpath(".//em/@title").extract_first()
        	item["title"] = product.xpath('.//div[@class="productTitle productTitle-spu"]').xpath(".//a/@title").extract_first()
        	item["shop"] = product.xpath('.//div[@class="productShop"]').xpath('.//a/text()').extract_first()
        	item["sale_amount"] = product.xpath('.//p[@class="productStatus"]').xpath('.//em/text()').extract_first()
        	#logging.info(str(item))

        	f.write(("%s %s %s %s %s\n\n" % (item["data_id"], item["price"], item["title"], item["shop"], item["sale_amount"])))
        	yield item

