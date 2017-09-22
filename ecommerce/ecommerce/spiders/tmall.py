# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy
import logging
import json
import time
import csv

class TmallSpider(scrapy.Spider):
    name = 'tmall'
    allowed_domains = ['tmall.com']
    url_host = "https://list.tmall.com"
    url_path = "/search_product.htm?q="
    start_urls = [
        #'https://list.tmall.com/search_product.htm?sort=d&q=apple',
        'https://www.tmall.com',
    ]
    seq = 0
    cat_data = {}
    fout = open('goods.data', 'w')
    fieldsname = ['CatId', 'BrandId', 'PageNo', 'Title', 'Url', 'Price', 'Sold', 'ShopName', 'ShopId', 'Location']
    csv_writer = csv.DictWriter(fout, fieldsname)
    csv_writer.writeheader()
    fout_raw = open('goods_list.data', 'w')

    cat_brand_file = 'brand_cat_search.csv'

    ff = open(cat_brand_file)
    f = open('brand_all.csv')
    for row in f:
        logging.info('1111111111 '+str(row))
    cat_brand_reader = csv.DictReader(ff)
    for row in cat_brand_reader:
        logging.info('000000000 ' + str(row))

    cat_brand_set = set()

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

    #user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Mobile Safari/537.36"

    def parse_raw_cookie(self):
        cookies = self.raw_cookie.strip().split(";")
        res = {}
        for c in cookies:
            kv = c.strip().split('=')
            res[kv[0].strip()] = kv[1].strip()
        return res

    def start_request(self):

        yield scrapy.Request(
            url = self.start_urls[0],
            headers = self.hheaders,
            #cookies = self.cookie,
            callback = self.parse)

    def parse(self, response):
        return self.get_goods_by_catid_and_brandid()

    def get_goods_by_catid_and_brandid(self):

        #brand_id_dict = {}
        #with open('brand_match_search.csv') as readf:
        #    readr = csv.DictReader(readf)
        #    for row in readr:
        #        brand_id_dict[row['BrandId']] = row
        logging.info('---------- get goods')

        for row in self.cat_brand_reader:
            logging.info('--------------' + str(row))
            cat_id = str(row['CatId'])
            brand_id = str(row['BrandId'])

            cat_brand_id = cat_id + "_"+ brand_id
            if cat_brand_id in cat_brand_set:
                continue
            else:
                cat_brand_set.add(cat_brand_id)

            #if brand_id not in brand_id_dict:
            #    continue

            url = 'https://list.tmall.com/m/search_items.htm?style=list'            
            url += '&brand=' + brand_id
            if len(cat_id) > 0:
                url += '&cat=' + cat_id

            req = scrapy.Request(url = url, headers = self.hheaders, callback = self.parse_goods_list)
            req.meta['brand_id'] = brand_id
            req.meta['cat_id'] = cat_id
            req.meta['page_no'] = 1

            yield req


    def parse_goods_list(self, response):
        brand_id = response.meta['brand_id']
        cat_id = response.meta['cat_id']
        page_no = response.meta['page_no']

        data = unicode(response.body, errors = 'replace')
        j = json.loads(data)

        self.fout_raw.write(json.dumps({'brand_id':brand_id, 'cat_id':cat_id, 'page_no':page_no, 'goods':j}) + "\n")

        for item in j['item']:
            goods = {} #TmallCatBrandGoodsItem()

            goods['BrandId'] = brand_id
            goods['CatId'] = cat_id
            goods['PageNo'] = page_no
            goods['Title'] = item['title']
            goods['Url'] = item['url']
            goods['Price'] = item['price']
            goods['Sold'] = item['sold']
            goods['ShopName'] = item['shop_name']
            goods['ShopId'] = item['shop_id']
            goods['Location'] = item['location']

            self.csv_writer.writerow(goods)
            #self.fout.write(json.dumps(goods) + '\n')

        total_page = j['total_page']
        total_results = j['total_results']

        if page_no < total_page:
            page_no += 1
            url = 'https://list.tmall.com/m/search_items.htm?style=list'
            if len(cat_id) > 0:
                url += '&cat=' + cat_id
            url += '&brand=' + brand_id
            url += '&page_no=' + str(page_no)
            req = scrapy.Request(url = url, headers = self.hheaders, callback = self.parse_goods_list)
            req.meta['brand_id'] = brand_id
            req.meta['cat_id'] = cat_id
            req.meta['page_no'] = page_no
            yield req



