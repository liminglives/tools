# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy
import logging
import json
import time
import csv
import urllib
import datetime

#self.fieldnames = ['BrandId', 'BrandName', 'CatId', 'CatName', "FinancialType", 'ProductName', "BloombergTicker"]

class TmallBrandToCatItem(scrapy.Item):
    BrandId = scrapy.Field()
    BrandName = scrapy.Field()
    Brand = scrapy.Field()
    CatId = scrapy.Field()
    CatName = scrapy.Field()
    FinancialType = scrapy.Field()
    ProductName = scrapy.Field()
    BloombergTicker = scrapy.Field()
    url = scrapy.Field()

class TmallBrandCatSearchSpider(scrapy.Spider):
    name = 'tmall_brand_to_cat'
    allowed_domains = ['tmall.com']
    url_host = "https://list.tmall.com"
    url_path = "/search_product.htm?q="
    start_urls = [
        #'https://list.tmall.com/search_product.htm?sort=d&q=apple',
        'https://www.tmall.com',
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,
        'ITEM_PIPELINES':{
            'ecommerce.pipelines.DataFrameExportPipeline': 400,
         },
    }

    brand_cat_writer = None
    brand_match_search_writer = None
    brand_unmatch_search_writer = None
    headers2 = ["ProductName","Bloomberg Ticker","Brand","Store Type","SWA_Category 1","SWA_Category 2","YearMonth","Year","Month","Sales Unit","Sales Value"]

    hheaders = {
        #"authority":"list.tmall.com",
        #"method":"GET",
        #"path":"/search_product.htm?sort=d&q=apple",
        "scheme":"https",
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding":"gzip, deflate, sdch, br",
        "accept-language":"zh-CN,zh;q=0.8",
        "upgrade-insecure-requests":"1",
        "Cache-control":"max-age=0",
        #"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
        "referer":"https://list.tmall.com/",
    }

    cookies = '_med=dw:1600&dh:900&pw:1600&ph:900&ist:0; x=__ll%3D-1%26_ato%3D0; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; _m_h5_tk=4cb87896fa3e2642155cec8b438f063a_1505902901233; _m_h5_tk_enc=2856eb7faab1c280da1bbde6a98d889f; l=ArS04LLut-CdwVfxKgUpbBTxBGkmjdh3; hng=;uc3=sg2=BxJP6B4LIzYp%2BV%2FeLdBOLaNf0NmeFCORECuWx8Ma3M8%3D&nk2=D8rrz16wbO1El74%3D&id2=UUBYjOisWsBJ&vt3=F8dBzWjIBaCuVky0N1w%3D&lg2=UtASsssmOIJ0bQ%3D%3D; tracknick=liminglives; _l_g_=Ug%3D%3D; ck1=; unb=280885558; lgc=liminglives; cookie1=UteENoRLXAOT%2BQe4R3C3NjlYJE5myu%2FmfsWEhtDjoqc%3D; login=true; cookie17=UUBYjOisWsBJ; cookie2=1a2567888b15a3722be9e2ee85c7dfd7; _nk_=liminglives; t=160b81ebbba3d0e1ebf6bdcc3767a4ec;uss=VqglGTe%2F5%2BhtUjSaGknHfeK1MMviMewwJzoQJXkvDrKk7e%2FHTYIyVJEknsY%3D; skt=f1398af28acff111; _tb_token_=33f7b87733376; cq=ccp%3D0; cna=VtDTERQLnmwCAXbyG241gYgV; isg=AoeH6hYPkt3MOhYjRe61MLkkFjuRJJMq0B27x1l0o5Y9yKeKYVzrvsWCHL5t'

    #user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Mobile Safari/537.36"

    def __init__(self, conf_file=None):
        super(TmallBrandCatSearchSpider, self).__init__()

        today = datetime.datetime.now().strftime('%F')
        self.date = today
        self.date_set = set([today,])


    def parse_raw_cookie(self, cookie):
        cookies = cookie.strip().split(";")
        res = {}
        for c in cookies:
            kv = c.strip().split('=')
            res[kv[0].strip()] = kv[1].strip()
        return res


    def start_request(self):
        logging.info('================== start request')

        yield scrapy.Request(
            url = self.start_urls[0],
            headers = self.hheaders,
            #cookies = self.parse_raw_cookie(self.cookies),
            callback = self.parse)

    def parse(self, response):
        logging.info('66666666666666 proxy:' + str(response.meta.get('proxy', None)))
        self.brand_cate_search_f = open('brand_cat_search_all.csv', 'wb')
        self.fieldnames = ['BrandId', 'BrandName', 'Brand', 'CatId', 'CatName', "FinancialType", 'ProductName', "BloombergTicker", "url"]
        self.brand_cat_writer = csv.DictWriter(self.brand_cate_search_f, fieldnames = self.fieldnames)
        self.brand_cat_writer.writeheader()

        return self.get_catid_by_brandid()


    def get_param_from_url(self, url, key):
        key += '='
        idx = url.find(key)
        if idx == -1:
            return None
        idx += len(key)
        end = url[idx:].find('&')
        val = url[idx:] if end == -1 else url[idx : idx + end]
        return val

    def get_catid_by_brandid(self):
        #brand_f = open('brand_match_all.csv')
        #brand_f = open('tmall_brand_search_TmallBrandMatchSearchItem_2017-10-11_1507710901.csv')
        brand_f = open('allchecked/brand_match_merged_all_checked.csv')
        reader = csv.DictReader(brand_f)

        for row in reader:
            url_list = []

            url_raw = "https://list.tmall.com/m/search_items.htm?"
            data = {"brand":row['BrandId']}
            url = url_raw + urllib.urlencode(data)
            url_list.append(url)

            brand_name = row['BrandName']
            search_brand = brand_name
            brands = brand_name.split('/')
            if len(brands) == 2:
                search_brand = brands[1].strip()
            data = {"brand":row['BrandId'], "q":search_brand}
            url2 = url_raw + urllib.urlencode(data)
            url_list.append(url2)

            for u in url_list:
                context = {}
                context['row'] = row
                context['url'] = u

                req = scrapy.Request(url = u, headers = self.hheaders,
                        #cookies = self.parse_raw_cookie(self.cookies),
                        callback = self.parse_search_result)
                req.meta['context'] = context

                yield req



    def parse_search_result(self, response):
        if response.status != 200:
            logging.info('============= response status '+str(response.status))
            return
        try:
            context = response.meta['context']
            data = unicode(response.body, errors = 'replace')
            j = json.loads(data)
        except:
            url = context['url']
            req = scrapy.Request(url = url, headers = self.hheaders,
                    #cookies = self.parse_raw_cookie(self.cookies),
                    callback = self.parse_search_result)
            req.meta['context'] = context
            req.meta['change_proxy'] = True
            yield req

        brand_list = j['brand_list']
        cat_list = j['cat_list']

        if len(brand_list) == 0:
            logging.critical('no brand:' + json.dumps(context))
        elif len(brand_list) == 1:
            brand_name_searched = brand_list[0]['brand_name']
            brand_id_searched = brand_list[0]['brand_id']
            for cat in cat_list:
                info= {}
                info['BrandName'] = brand_name_searched
                info['BrandId'] = brand_id_searched
                info['CatName'] = cat['cat_name']
                info['CatId'] = cat['cat_id']
                info['FinancialType'] = 'Stock'
                info['BloombergTicker'] = context['row']['BloombergTicker']
                info['ProductName'] = context['row']['ProductName']
                info['Brand'] = context['row']['Brand']
                info['url'] = context['url']
                self.brand_cat_writer.writerow(info)

                info = TmallBrandToCatItem()
                info['BrandName'] = brand_name_searched
                info['BrandId'] = brand_id_searched
                info['CatName'] = cat['cat_name']
                info['CatId'] = cat['cat_id']
                info['FinancialType'] = 'Stock'
                info['BloombergTicker'] = context['row']['BloombergTicker']
                info['ProductName'] = context['row']['ProductName']
                info['Brand'] = context['row']['Brand']
                info['url'] = context['url']
                yield info

            if len(cat_list) == 0:
                info= {}
                info['BrandName'] = brand_name_searched
                info['BrandId'] = brand_id_searched
                info['CatName'] = ""
                info['CatId'] = ""
                info['FinancialType'] = 'Stock'
                info['BloombergTicker'] = context['row']['BloombergTicker']
                info['ProductName'] = context['row']['ProductName']
                info['Brand'] = context['row']['Brand']
                info['url'] = context['url']
                self.brand_cat_writer.writerow(info)

                info = TmallBrandToCatItem()
                info['BrandName'] = brand_name_searched
                info['BrandId'] = brand_id_searched
                info['CatName'] = ""
                info['CatId'] = ""
                info['FinancialType'] = 'Stock'
                info['BloombergTicker'] = context['row']['BloombergTicker']
                info['ProductName'] = context['row']['ProductName']
                info['Brand'] = context['row']['Brand']
                info['url'] = context['url']
                yield info
        else:
            logging.error('unknown question:' + context['url'])






