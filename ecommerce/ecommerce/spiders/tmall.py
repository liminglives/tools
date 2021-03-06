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
    ProductName = scrapy.Field()
    FinancialType = scrapy.Field()
    BloombergTicker = scrapy.Field()

    PageNo = scrapy.Field()
    Title = scrapy.Field()
    Url = scrapy.Field()
    Price = scrapy.Field()
    Sold = scrapy.Field()
    ShopName = scrapy.Field()
    ShopId = scrapy.Field()
    RealShopId = scrapy.Field()
    SellerId = scrapy.Field()
    Location = scrapy.Field()

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
    name = 'tmall_goods_list'
    allowed_domains = ['tmall.com']
    url_host = "https://list.tmall.com"
    url_path = "/search_product.htm?q="
    start_urls = [
        #'https://list.tmall.com/search_product.htm?sort=d&q=apple',
        'https://www.tmall.com',
    ]
    seq = 0
    cat_data = {}
    cat_brand_set = set()

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
        "referer":"https://list.tmall.com/search_product.htm?q=%C2%B6%C2%B6&type=p&tmhkh5=&spm=a220m.6910245.a2227oh.d100&from=mallfp..m_1_searchbutton",
    }

    cookies = '_med=dw:1600&dh:900&pw:1600&ph:900&ist:0; x=__ll%3D-1%26_ato%3D0; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; _m_h5_tk=4cb87896fa3e2642155cec8b438f063a_1505902901233; _m_h5_tk_enc=2856eb7faab1c280da1bbde6a98d889f; l=ArS04LLut-CdwVfxKgUpbBTxBGkmjdh3; hng=;uc3=sg2=BxJP6B4LIzYp%2BV%2FeLdBOLaNf0NmeFCORECuWx8Ma3M8%3D&nk2=D8rrz16wbO1El74%3D&id2=UUBYjOisWsBJ&vt3=F8dBzWjIBaCuVky0N1w%3D&lg2=UtASsssmOIJ0bQ%3D%3D; tracknick=liminglives; _l_g_=Ug%3D%3D; ck1=; unb=280885558; lgc=liminglives; cookie1=UteENoRLXAOT%2BQe4R3C3NjlYJE5myu%2FmfsWEhtDjoqc%3D; login=true; cookie17=UUBYjOisWsBJ; cookie2=1a2567888b15a3722be9e2ee85c7dfd7; _nk_=liminglives; t=160b81ebbba3d0e1ebf6bdcc3767a4ec;uss=VqglGTe%2F5%2BhtUjSaGknHfeK1MMviMewwJzoQJXkvDrKk7e%2FHTYIyVJEknsY%3D; skt=f1398af28acff111; _tb_token_=33f7b87733376; cq=ccp%3D0; cna=VtDTERQLnmwCAXbyG241gYgV; isg=AoeH6hYPkt3MOhYjRe61MLkkFjuRJJMq0B27x1l0o5Y9yKeKYVzrvsWCHL5t'

    def __init__(self, start_urls_file=None, *args, **kwargs):
        super(TmallGoodsListSpider, self).__init__()

        today = datetime.datetime.now().strftime('%F')
        self.date = today
        self.date_set = set([today,])

        #self.fout = open('goods.data_failed', 'wb')
        #self.fieldsname = ['CatId', 'CatName', 'BrandId', 'BrandName', 'ProductName', 'FinancialType', 'BloombergTicker', 'PageNo', 'Title', 'Url', 'Price', 'Sold', 'ShopName', 'ShopId', 'Location']
        #self.csv_writer = csv.DictWriter(self.fout, self.fieldsname)
        #self.csv_writer.writeheader()
        self.fout_raw = open('goods_list_raw.data', 'w')

        #self.cat_brand_file = 'brand_cat_search_all.csv'
        self.cat_brand_file = 'ls/brand_cat_pc.csv'
        self.ff = open(self.cat_brand_file)
        self.cat_brand_reader = csv.DictReader(self.ff)


        self.auto_crawl = True
        if start_urls_file:
            self.auto_crawl = False
            with open(start_urls_file) as f:
                self.start_urls2 = []
                for url in f:
                    url = url.strip()
                    self.start_urls2.append(url)
            self.cat_brand_dict = {}
            for row in self.cat_brand_reader:
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
                #cookies = self.parse_raw_cookie(self.cookies),
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

        for row in self.cat_brand_reader:

            cat_id = str(row['CatId'])
            brand_id = str(row['BrandId'])

            cat_brand_id = cat_id + "_"+ brand_id
            if cat_brand_id in self.cat_brand_set:
                continue
            else:
                self.cat_brand_set.add(cat_brand_id)

            #if brand_id not in brand_id_dict:
            #    continue

            url = 'https://list.tmall.com/m/search_items.htm?'
            url += '&brand=' + brand_id
            if len(cat_id) > 0:
                url += '&cat=' + cat_id

            req = scrapy.Request(url = url,
                    headers = self.hheaders,
                    #cookies = self.parse_raw_cookie(self.cookies),
                    callback = self.parse_goods_list)
            req.meta['brand_id'] = brand_id
            req.meta['cat_id'] = cat_id
            req.meta['page_no'] = 1
            req.meta['row'] = row

            yield req


    def parse_goods_list(self, response):
        logging.info('1111111111119999999999999999999999999999999999999999')
        brand_id = response.meta['brand_id']
        cat_id = response.meta['cat_id']
        page_no = response.meta['page_no']
        row = response.meta['row']

        data = unicode(response.body, errors = 'replace')
        j = json.loads(data)

        self.fout_raw.write(json.dumps({'brand_id':brand_id, 'cat_id':cat_id, 'page_no':page_no, 'goods':j}) + "\n")

        for item in j['item']:
            goods = {} #TmallCatBrandGoodsItem()

            goods['BrandId'] = brand_id
            goods['BrandName'] = row['BrandName']
            goods['CatId'] = cat_id
            goods['CatName'] = row['CatName']
            goods['FinancialType'] = row['FinancialType']
            goods['ProductName'] = row['ProductName']
            goods['BloombergTicker'] = row['BloombergTicker']

            goods['PageNo'] = page_no
            goods['Title'] = item['title']
            goods['Url'] = item['url']
            goods['Price'] = item['price']
            goods['Sold'] = item['sold']
            goods['ShopName'] = item['shop_name']
            goods['ShopId'] = item['shop_id']
            goods['RealShopId'] = item['real_shop_id']
            goods['SellerId'] = item['seller_id']
            goods['Location'] = item['location']

            #self.csv_writer.writerow(goods)
            #self.fout.write(json.dumps(goods) + '\n')

            goods = TmallGoodsItem()
            goods['BrandId'] = brand_id
            goods['BrandName'] = row['BrandName']
            goods['CatId'] = cat_id
            goods['CatName'] = row['CatName']
            goods['FinancialType'] = row['FinancialType']
            goods['ProductName'] = row['ProductName']
            goods['BloombergTicker'] = row['BloombergTicker']

            goods['PageNo'] = page_no
            goods['Title'] = item['title']
            goods['Url'] = item['url']
            goods['Price'] = item['price']
            goods['Sold'] = item['sold']
            goods['ShopName'] = item['shop_name']
            goods['ShopId'] = item['shop_id']
            goods['RealShopId'] = item['real_shop_id']
            goods['SellerId'] = item['seller_id']
            goods['Location'] = item['location']
            yield goods


        total_page = int(j['total_page'])
        total_results = j['total_results']

        if page_no < total_page:
            page_no += 1
            url = 'https://list.tmall.com/m/search_items.htm?style=list&type=p&tmhkh5=&spm=a223j.8443192.a2227oh.d100&from=mallfp..m_1_searchbutton'
            if len(cat_id) > 0:
                url += '&cat=' + cat_id
            url += '&brand=' + brand_id
            url += '&page_no=' + str(page_no)
            req = scrapy.Request(url = url,
                    headers = self.hheaders,
                    #cookies = self.parse_raw_cookie(self.cookies),
                    callback = self.parse_goods_list)
            req.meta['brand_id'] = brand_id
            req.meta['cat_id'] = cat_id
            req.meta['page_no'] = page_no
            req.meta['row'] = row
            yield req

    def merge_goods(self, goods_list):
        goods_dict = {}
        for goods in goods_list:
            catid = goods['CatId']
            brandid = goods['BrandId']
            k = str(brandid) + "_" + str(catid)
            sold = (goods['Sold'])
            price = float(goods['Price'])
            if not sold.isdigit():
                if sold_wan_unit in sold:
                    n = sold[:len(sold) - len(sold_wan_unit)]
                    sold = float(n)
                    sold = int(sold * 10000)
                    sold += 500
                else:
                    logging.info(goods)
                    continue
            else:
                sold = int(sold)
            if k in goods_dict:
                item = goods_dict[k]
                item['SalesUnit'] += sold
                item['SalesValue'] += sold * price
            else:
                item = TmallGoodsMergedItem()
                item['BrandId'] = goods['BrandId']
                item['BrandName'] = goods['BrandName']
                item['CatId'] = goods['CatId']
                item['CatName'] = goods['CatName']
                item['FinancialType'] = goods['FinancialType']
                item['ProductName'] = goods['ProductName']
                item['BloombergTicker'] = goods['BloombergTicker']
                item['SalesUnit'] = sold
                item['SalesValue'] = sold * price
                goods_dict[k] = item

        return goods_dict




