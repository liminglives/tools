# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import scrapy
import logging
from ecommerce.items import EcommerceItem
from ecommerce.items import TmallCategory,TmallCatBrandItem,TmallCatBrandGoodsItem
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
    cat_brand_file = 'brand_cat_search.csv'#'cat_brand.csv'

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

    def start_requestss(self):

        yield scrapy.Request(
            url = self.start_urls[0],
            headers = self.hheaders,
            #cookies = self.cookie,
            callback = self.parse)

    def parse(self, response):
        return self.get_goods_by_catid_and_brandid()


    def parse_homepage(self, response):
        logging.info('111111====================')
        data = response.xpath('//*[@id="J_defaultData"]').xpath('text()').extract_first()
        data = data.strip()
        #logging.info(data)

        j = json.loads(data)

        d = j['page']['100']

        j_main_cat = d['categoryMainLines']
        self.cat_data['main_cat'] = j_main_cat
        main_cat_size = len(j_main_cat)
        self.cat_data = j_main_cat

        sub_cat_hotword = {}
        for item in d:
            if 'hotWordType' in item:
                seq = int(item[len('hotWordType'):])
                logging.info('hotwordtype'+str(seq))
                sub_cat_hotword[seq] = d[item]

        for i in xrange(main_cat_size):
            cat = TmallCategory()

            main_cat = j_main_cat[i]
            sub_cats = sub_cat_hotword[i + 1]
            title = ""
            for c in main_cat:
                if len(c) > len('title') and c[0:len('title')] == 'title' and len(main_cat[c]) > 0:
                    if title != '':
                        title += '/'
                    title += main_cat[c]
            main_cat['title'] = title

            #main_cat['sub_cats'] = sub_cats
            appids = []
            cat['main_cat'] = main_cat
            cat['sub_cat'] = sub_cats
            for sub_cat in sub_cats:
                if sub_cat['isUse']:
                    appids.append(str(sub_cat['appId']))

            subcat_hotword_url = 'https://aldh5.tmall.com/recommend2.htm?notNeedBackup=true&appId=' + (','.join(appids))
            main_cat['subcat_hotword_url'] = subcat_hotword_url
            cat['subcat_hotword_url'] = subcat_hotword_url

            req = scrapy.Request(
                url = subcat_hotword_url,
                headers = self.hheaders,
                callback = self.recommend_parse)
            req.meta['cat'] = cat

            #self.request(main_cat)

            yield req
            break


    def request(self, main_cat):
        req = scrapy.Request(
            url = main_cat['subcat_hotword_url'],
            headers = self.hheaders,
            callback = self.recommend_parse)
        req.meta['cat'] = main_cat
        return req

    def get_param_from_url(self, url, key):
        key += '='
        idx = url.find(key)
        if idx == -1:
            return None
        idx += len(key)
        end = url[idx:].find('&')
        val = url[idx:] if end == -1 else url[idx : idx + end]
        return val

    def recommend_parse(self, response):
        logging.info('999999999999999')
        data = unicode(response.body, errors = 'replace')
        j = json.loads(data)
        cat = response.meta['cat']
        #cat['subcat_hotword'] = j
        cat['subcat_hotword'] = j



        subcat_map = {}
        for subcat in cat['sub_cat']:
            subcat_map[subcat['appId']] = subcat

        cat['hotword_brand'] = {}
        for appid in j:
            data = j[appid]['data']
            for item in data:
                context = {}
                context['main_cat'] = cat['main_cat']
                context['appid'] = appid
                context['sub_cat'] = subcat_map[appid]
                context['sub_cat_hotword'] = item
                url = item['action']

                cat_no = self.get_param_from_url(url, 'cat')
                if not cat_no:
                    continue
                get_brand_from_cat_url = 'https://list.tmall.com/ajax/allBrandShowForGaiBan.htm?t=0&sort=s&style=g&search_condition=2&from=sn_1_cat-qp'

                get_brand_from_cat_url += "&cat=" + str(cat_no)
                industry_cat_no = self.get_param_from_url(url, 'industryCatId')
                cat['hotword_brand'][cat_no] = item

                if industry_cat_no:
                    get_brand_from_cat_url += '&industryCatId=' + str(industry_cat_no)

                item['brand_url'] = get_brand_from_cat_url
                context['cat'] = cat_no

                req = scrapy.Request(url = get_brand_from_cat_url, headers = self.hheaders, callback = self.parse_brand)
                req.meta['context'] = context

                yield req

        pass

    def parse_brand(self, response):
        logging.info('brand 8888888888888888888')
        data = unicode(response.body, errors = 'replace')
        j = json.loads(data)
        context = response.meta['context']
        #context['brand'] = j
        item = TmallCatBrandItem()
        item['main_cat'] = context['main_cat']
        item['sub_cat'] = context['sub_cat']
        item['sub_cat_hotword'] = context['sub_cat_hotword']
        item['cat_id'] = context['cat']
        item['appid'] = context['appid']
        #item['brands'] = context['brand']

        for brand in j:
            brand_name = brand['title']
            href = brand['href']
            brand_id = self.get_param_from_url(href, 'brand')
            if brand_id is None:
                continue
            url = 'https://list.tmall.com/m/search_items.htm?style=list'
            url += '&cat=' + context['cat']
            url += '&brand=' + brand_id

            req = scrapy.Request(url = url, headers = self.hheaders, callback = self.parse_goods_list)
            req.meta['context'] = context
            req.meta['brand_name'] = brand_name
            req.meta['brand_id'] = brand_id
            req.meta['page_no'] = 1

            yield req

    def get_goods_by_catid_and_brandid(self):
        f = open(self.cat_brand_file)
        r = csv.DictReader(f)
        brand_id_dict = {}
        with open('brand_match_search.csv') as readf:
            readr = csv.DictReader(readf)
            for row in readr:
                brand_id_dict[row['BrandId']] = row

        for row in r:
            cat_id = str(row['CatId'])
            brand_id = str(row['BrandId'])

            cat_brand_id = cat_id + "_"+ brand_id
            if cat_brand_id in cat_brand_set:
                continue
            else:
                cat_brand_set.add(cat_brand_id)

            if brand_id not in brand_id_dict:
                continue

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



