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

class TmallSpider(scrapy.Spider):
    name = 'tmall_brand_search'
    allowed_domains = ['tmall.com']
    url_host = "https://list.tmall.com"
    url_path = "/search_product.htm?q="
    start_urls = [
        #'https://list.tmall.com/search_product.htm?sort=d&q=apple',
        'https://www.tmall.com',
    ]


    brand_cat_writer = None
    brand_match_search_writer = None
    brand_unmatch_search_writer = None

    brand_cate_search_f = open('brand_cat_search.csv', 'wb')
    fieldnames = ['BrandId', 'BrandName', 'CatId', 'CatName']
    brand_cat_writer = csv.DictWriter(brand_cate_search_f, fieldnames = fieldnames)
    brand_cat_writer.writeheader()

    headers = ['Key', 'BrandId', 'BrandName', 'Brand', "FinancialType", 'ProductName', "BloombergTicker"]
    brand_match_search_f = open('brand_match_search.csv', 'wb')
    brand_match_search_writer = csv.DictWriter(brand_match_search_f, headers)
    brand_match_search_writer.writeheader()

    headers2 = ["ProductName","Bloomberg Ticker","Brand","Store Type","SWA_Category 1","SWA_Category 2","YearMonth","Year","Month","Sales Unit","Sales Value"]
    unmatch_f = open('brand_unmatch_search.csv', 'wb')
    brand_unmatch_search_writer = csv.DictWriter(unmatch_f, headers2)
    brand_unmatch_search_writer.writeheader()

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

    #user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Mobile Safari/537.36"

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
            cookies = self.parse_raw_cookie(self.cookies),
            callback = self.parse)

    def parse(self, response):
        return self.get_brandid_and_catid_by_brandname()


    def get_param_from_url(self, url, key):
        key += '='
        idx = url.find(key)
        if idx == -1:
            return None
        idx += len(key)
        end = url[idx:].find('&')
        val = url[idx:] if end == -1 else url[idx : idx + end]
        return val

    def get_brandid_and_catid_by_brandname(self):
        brand_f = open('brand_unmatch_raw.csv')
        reader = csv.DictReader(brand_f)



        for row in reader:
            info = {}
            for k in self.headers2:
                info[k] = row[k]

            row = info

            brand = row['Brand'].strip()
            search_brand = brand
            brand_en = None
            brand_cn = None
            brands = brand.split('/')
            if len(brands) == 2:
                brand_en = brands[0].strip()
                brand_cn = brands[1].strip()
                search_brand = brand_cn

            url = "https://list.tmall.com/m/search_items.htm?"
            data = {"q":search_brand}
            url += urllib.urlencode(data)
            context = {}
            context['row'] = row
            context['search_brand'] = search_brand
            context['brand'] = brand.lower()
            context['brand_en'] = brand_en.lower() if brand_en else brand_en
            context['brand_cn'] = brand_cn

            req = scrapy.Request(url = url, headers = self.hheaders, cookies = self.parse_raw_cookie(self.cookies), callback = self.parse_search_result)
            req.meta['context'] = context

            yield req



    def parse_search_result(self, response):
        if response.status != 200:
            logging.info('============= response status '+str(response.status))
            return
        context = response.meta['context']
        data = unicode(response.body, errors = 'replace')
        j = json.loads(data)

        brand_list = j['brand_list']
        cat_list = j['cat_list']

        if len(brand_list) == 0:
            if len(j['minisites']) > 0:
                brand_id_searched = j['minisites'][0]['id']
                brand_name_searched = context['search_brand']
                info = {}
                info['Key'] = context['search_brand']
                info['Brand'] = context['row']['Brand']
                info['FinancialType'] = 'Stock'
                info['BloombergTicker'] = context['row']['Bloomberg Ticker']
                info['ProductName'] = context['row']['ProductName']
                info['BrandName'] = brand_name_searched
                info['BrandId'] = brand_id_searched
                self.brand_match_search_writer.writerow(info)   

                for cat in cat_list:
                    info= {}
                    info['BrandName'] = brand_name_searched
                    info['BrandId'] = brand_id_searched
                    info['CatName'] = cat['cat_name']
                    info['CatId'] = cat['cat_id']
                    self.brand_cat_writer.writerow(info)
                if len(cat_list) == 0:
                    info= {}
                    info['BrandName'] = brand_name_searched
                    info['BrandId'] = brand_id_searched
                    info['CatName'] = ""
                    info['CatId'] = ""
                    self.brand_cat_writer.writerow(info) 
            else:
                logging.critical('no brand:' + json.dumps(context))
                self.brand_unmatch_search_writer.writerow(context['row'])
        elif len(brand_list) == 1:
            brand_name_searched = brand_list[0]['brand_name']
            brand_id_searched = brand_list[0]['brand_id']
            #if brand_name_searched.lower() == context['brand'] or brand_name_searched == context['brand_cn'] or brand_name_searched == context['brand_en']:
            if True:
                info = {}
                info['Key'] = context['search_brand']
                info['Brand'] = context['row']['Brand']
                info['FinancialType'] = 'Stock'
                info['BloombergTicker'] = context['row']['Bloomberg Ticker']
                info['ProductName'] = context['row']['ProductName']
                info['BrandName'] = brand_name_searched
                info['BrandId'] = brand_id_searched
                self.brand_match_search_writer.writerow(info)

                for cat in cat_list:
                    info= {}
                    info['BrandName'] = brand_name_searched
                    info['BrandId'] = brand_id_searched
                    info['CatName'] = cat['cat_name']
                    info['CatId'] = cat['cat_id']
                    self.brand_cat_writer.writerow(info)
                if len(cat_list) == 0:
                    info= {}
                    info['BrandName'] = brand_name_searched
                    info['BrandId'] = brand_id_searched
                    info['CatName'] = ""
                    info['CatId'] = ""
                    self.brand_cat_writer.writerow(info)
            else:
                logging.critical('=====================not full match:' + json.dumps(context))
                self.brand_unmatch_search_writer.writerow(context['row'])
        else:
            hit = False
            minisite = None
            if len(j['minisites']) > 0:
                minisite = j['minisites'][0]
            brandid = None
            for brand in brand_list:
                if minisite != None and brand['brand_id'] == minisite['id']: 
                    brandid = brand['brand_id']
                    hit = True
                    break
                if brand['brand_name'].lower().strip() == context['brand']:
                    brandid = brand['brand_id']
                    hit = True
                    break
                if brand['brand_name'].lower().strip() == context['search_brand']:
                    brandid = brand['brand_id']
                    hit = True
                    break

                else:
                    continue
                    logging.critical('=====================filter match:' + json.dumps(context))

            if not hit:
                self.brand_unmatch_search_writer.writerow(context['row'])
            else:
                url = "https://list.tmall.com/m/search_items.htm?brand="
                url += str(brandid)
                context['search_brand'] += "_" + str(brandid)
                req = scrapy.Request(url = url, headers = self.hheaders, cookies = self.parse_raw_cookie(self.cookies), callback = self.parse_search_result)
                req.meta['context'] = context
                yield req







