# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy
import logging
import json
import time
import csv
import datetime
import urlparse

#self.fieldsname = ['CatId', 'BrandId', 'PageNo', 'Title', 'Url', 'Price', 'Sold', 'ShopName', 'ShopId', 'Location']
class TmallGoodsItem(scrapy.Item):
    CatId = scrapy.Field()
    CatName = scrapy.Field()
    BrandId = scrapy.Field()
    BrandName = scrapy.Field()

    SellerId = scrapy.Field()

    Title = scrapy.Field()
    Url = scrapy.Field()
    Price = scrapy.Field()
    TotalSoldQuantity = scrapy.Field()

class TmallGoodsMergedItem(scrapy.Item):
    CatId = scrapy.Field()
    CatName = scrapy.Field()
    BrandId = scrapy.Field()
    BrandName = scrapy.Field()
    ProductName = scrapy.Field()
    FinancialType = scrapy.Field()
    BloombergTicker = scrapy.Field()

    SalesValue = scrapy.Field()
    SalesUnit = scrapy.Field()


class TmallGoodsListSpider(scrapy.Spider):
    name = 'tmall_goods_list_total_pcweb'
    allowed_domains = ['tmall.com']
    url_host = "https://list.tmall.com"
    url_path = "/search_product.htm?q="
    start_urls = [
        #'https://list.tmall.com/search_product.htm?sort=d&q=apple',
        'https://www.tmall.com',
    ]
    seq = 0
    cat_data = {}
    cat_shop_set = set()

    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,
        'ITEM_PIPELINES':{
            'ecommerce.pipelines.DataFrameExportPipeline': 400,
         },
    }


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
        #"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
        #"referer":"https://list.tmall.com/search_product.htm?q=%C2%B6%C2%B6&type=p&tmhkh5=&spm=a220m.6910245.a2227oh.d100&from=mallfp..m_1_searchbutton",
    }

    #cookies = '_med=dw:1600&dh:900&pw:1600&ph:900&ist:0; x=__ll%3D-1%26_ato%3D0; l=AhcXMoGA5GniABQ4jXT6W5O4J5BhWuuP; swfstore=30363; sm4=310115; _m_h5_tk=579f13b283d2aa2a4875b661ef4cc54f_1508221649830; _m_h5_tk_enc=d136a04b8da748c167595ef8baffac7e; hng=CN%7Czh-CN%7CCNY%7C156;uc1=cookie14=UoTcBz3OBAjZQg%3D%3D&lng=zh_CN&cookie16=URm48syIJ1yk0MX2J7mAAEhTuw%3D%3D&existShop=false&cookie21=W5iHLLyFe3xm&tag=8&cookie15=URm48syIIVrSKA%3D%3D&pas=0; uc3=sg2=BxJP6B4LIzYp%2BV%2FeLdBOLaNf0NmeFCORECuWx8Ma3M8%3D&nk2=D8rrz16wbO1El74%3D&id2=UUBYjOisWsBJ&vt3=F8dBzLBNVq%2B14hz%2BJK0%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D; tracknick=liminglives; _l_g_=Ug%3D%3D; ck1=; unb=280885558; lgc=liminglives; cookie1=UteENoRLXAOT%2BQe4R3C3NjlYJE5myu%2FmfsWEhtDjoqc%3D; login=true;cookie17=UUBYjOisWsBJ; cookie2=7eb13bd90bd69c6b9c5c3e2ce5d73212; _nk_=liminglives; t=160b81ebbba3d0e1ebf6bdcc3767a4ec; uss=WqOkpW93Iq8F20N8FQL%2FXS2q3vKf4QwND%2FQJ8BvNZCNaCMrbgZVZHlUw4Z0%3D; skt=f5030b2b783b9e69; _tb_token_=8ee51360871d; cq=ccp%3D0; res=scroll%3A1583*5342-client%3A1583*794-offset%3A1583*5342-screen%3A1600*900;pnm_cku822=098%23E1hvMvvUvbpvUpCkvvvvvjiPP2LUAjtEPsqvAjD2PmPvzjnbPsqUtjtRP2qUQjlnP4wCvvBvpvpZ2QhvCPMMvvmtvpvIphvvvvvvB9XvpC9CvvC27ZCvVvhvvhPjphvOvpvvp1YvpC9CvvC2jTyCvv3vpvBYDmhnKgyCvvXmp99hV19EvpCWB2aBv8ROjovDN%2BBlDBhIoogW%2BE7reC69EcqhaXZBE6EkLixrV8gfN3%2Buac7JWsxfUlJDSLwZ4BUeowe9RqvAhkZOkjVTVjWxwAMxQvhCvvXvppvvvvvtvpvhphvvvv%3D%3D;otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; whl=-1%260%260%260; cna=VtDTERQLnmwCAXbyG241gYgV; isg=AhsbLvFPxkek-jrn8cLBPLXAqn9FWOexTHmXgw1bWZqU7D_OlMBVQqIs8HoZ'

    cookies = 't=ad0e1fb5cb8330156a17c144afd3e74f; _tb_token_=5ee5c7618d77; cookie2=1b351fe8054879f264b1ec598253a5a5; cna=U7BsErPnxXQCAXbyG25ZYoUK; isg=AsPDNogRns9GRlK7J4T1FfuAUoetkJ859LH_i_WgMyK7tOPWfQjnyqEmWHIB'

    def __init__(self, start_urls_file=None, *args, **kwargs):
        super(TmallGoodsListSpider, self).__init__()

        today = datetime.datetime.now().strftime('%F')
        self.date = today
        self.date_set = set([today,])

        #self.fout_raw = open('goods_list_failed.data', 'w')

        #self.cat_brand_file = 'brand_cat_search_all.csv'
        self.cat_brand_file = 'tmall_goods_list_2017-10-17_1508209889.csv'
        self.ff = open(self.cat_brand_file)
        self.cat_shop_reader = csv.DictReader(self.ff)


        self.auto_crawl = True
        if start_urls_file:
            self.auto_crawl = False
            with open(start_urls_file) as f:
                self.start_urls2 = []
                for url in f:
                    url = url.strip()
                    self.start_urls2.append(url)
            self.cat_brand_dict = {}
            for row in self.cat_shop_reader:
                cat_id = str(row['CatId'])
                brand_id = str(row['BrandId'])
                cat_brand_id = cat_id + "_"+ brand_id
                if cat_brand_id not in self.cat_brand_dict:
                    self.cat_brand_dict[cat_brand_id] = row
        print self.auto_crawl, start_urls_file

    def parse_raw_cookie(self, cookie):
        cookies = cookie.strip().split(";")
        res = {}
        for c in cookies:
            kv = c.strip().split('=')
            res[kv[0].strip()] = kv[1].strip()
        return res

    def parse_url_param(self, url):
        query = urlparse.urlparse(url).query
        return dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])

    def start_requests(self):

        logging.info('start request============')
        if self.auto_crawl:
            yield scrapy.Request(
                url = self.start_urls[0],
                headers = self.hheaders,
                cookies = self.parse_raw_cookie(self.cookies),
                callback = self.parse)
        else:
            for url in self.start_urls2:
                logging.info('9999999999999999999999999999999999999999')
                url_params = self.parse_url_param(url)
                brandid = url_params['brand']
                catid = url_params.get('cat', "")
                pageno = int(url_params.get('page_no', "1"))
                cat_brand_id = str(catid) + "_" + str(brandid)
                if cat_brand_id not in self.cat_brand_dict:
                    logging.error('cat_brand_id:'+cat_brand_id+" is not found")
                    continue
                row = self.cat_brand_dict[cat_brand_id]
                req = scrapy.Request(
                    url = url,
                    headers = self.hheaders,
                    #cookies = self.parse_raw_cookie(self.cookies),
                    callback = self.parse_goods_list)
                req.meta['brand_id'] = brandid
                req.meta['cat_id'] = catid
                req.meta['page_no'] = pageno
                req.meta['row'] = row
                yield req

    def parse(self, response):
        return self.get_goods_by_catid_and_brandid()

    def get_goods_by_catid_and_brandid(self):

        #brand_id_dict = {}
        #with open('brand_match_search.csv') as readf:
        #    readr = csv.DictReader(readf)
        #    for row in readr:
        #        brand_id_dict[row['BrandId']] = row
        #logging.info('---------- get goods')

        for row in self.cat_shop_reader:

            cat_id = str(row['CatId'])
            shop_id = str(row['ShopId'])
            seller_id = str(row['SellerId'])

            cat_shop_id = cat_id + '_' + seller_id
            if cat_shop_id in self.cat_shop_set or cat_id == '725677994':
                continue
            else:
                self.cat_shop_set.add(cat_shop_id)

            url = 'https://list.tmall.com/search_shopitem.htm?style=sg&sort=td&from=sn_1_cat'
            url += '&user_id=' + seller_id
            if len(cat_id) > 0:
                url += '&cat=' + cat_id

            req = scrapy.Request(url = url,
                    headers = self.hheaders,
                    cookies = self.parse_raw_cookie(self.cookies),
                    callback = self.parse_goods_list)
            req.meta['seller_id'] = seller_id
            req.meta['cat_id'] = cat_id
            req.meta['row'] = row

            yield req


    def parse_goods_list(self, response):
        seller_id = response.meta['seller_id']
        cat_id = response.meta['cat_id']
        row = response.meta['row']

        products = response.xpath('//*[@id="J_ItemList"]/div[@class="product"]')
        with open('tmall.html', 'w') as f:
            f.write(response.body)

        print '===', type(products), products

        for product in products:

            goods = TmallGoodsItem()
            goods['BrandId'] = row['BrandId']
            goods['BrandName'] = row['BrandName']
            goods['CatId'] = cat_id
            goods['CatName'] = row['CatName']

            goods['SellerId'] = seller_id
            #//*[@id="J_ItemList"]/div[1]/div/p[2]/a
            goods['Title'] = product.xpath('.//p[@class="productTitle"]').xpath(".//a/@title").extract_first()
            goods['Url'] = product.xpath('.//p[@class="productTitle"]').xpath(".//a/@href").extract_first()

            #//*[@id="J_ItemList"]/div[1]/div/p[1]/em/text()
            goods['Price'] = product.xpath('.//p[@class="productPrice"]').xpath(".//em/text()").extract_first()
            #//*[@id="J_ItemList"]/div[1]/div/p[3]/span[1]/em
            goods['TotalSoldQuantity'] = product.xpath('.//p[@class="productStatus"]').xpath('.//em/text()').extract_first()
            yield goods

        #//*[@id="J_bottomPage"]/div/div/b[1]/a[4]
        next_page = response.xpath('//*[@id="J_bottomPage"]/div/div/b[1]/a[@class="ui-page-next"]').xpath('.//@href').extract_first()

        print '====next_page', next_page,  response.xpath('//*[@id="J_bottomPage"]/div/div/b[1]').xpath('.//a[@class="ui-page-next"]')
        print response.xpath('//*[@id="J_bottomPage"]/div/div/b[1]/a')

        if next_page:
            para = self.parse_url_param(next_page)
            s = para.get('s', None)
            if s:
                url = 'https://list.tmall.com/search_shopitem.htm?style=sg&sort=td&from=sn_1_cat'
                url += '&user_id=' + seller_id
                url += '&s=' + s
                if len(cat_id) > 0:
                    url += '&cat=' + cat_id

                req = scrapy.Request(url = url,
                        headers = self.hheaders,
                        cookies = self.parse_raw_cookie(self.cookies),
                        callback = self.parse_goods_list)
                req.meta['seller_id'] = seller_id
                req.meta['cat_id'] = cat_id
                req.meta['row'] = row

                yield req





