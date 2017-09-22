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

class TmallSpider(scrapy.Spider):
    name = 'tmall2'
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
    fout_raw = open('goods_list.data', 'w')

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
    raw_cookie = '_med=dw:1600&dh:900&pw:1600&ph:900&ist:0; _m_h5_tk=fde939fe377b15f1c551ce3f335ff0f5_1504859336473; _m_h5_tk_enc=a0a8ef40316b0d74fcad605186544e61; _tb_token_=35e4be4d3333f; uc1=cookie14=UoTcC%2BSX%2F6mogg%3D%3D&lng=zh_CN&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D&existShop=false&cookie21=URm48syIYn73&tag=8&cookie15=WqG3DMC9VAQiUQ%3D%3D&pas=0; uc3=sg2=BxJP6B4LIzYp%2BV%2FeLdBOLaNf0NmeFCORECuWx8Ma3M8%3D&nk2=D8rrz16wbO1El74%3D&id2=UUBYjOisWsBJ&vt3=F8dBzWfTEYZatYka4co%3D&lg2=URm48syIIVrSKA%3D%3D; uss=UNaGsRU1vsCl%2FS4TE1qU3F751SR693k%2B6QhroEm42a%2FYqnLA%2FOEQOJ1z8s8%3D; lgc=liminglives; tracknick=liminglives; cookie2=3bfbdcf3f87b10727416f592e751eeea; sg=s8f; cookie1=UteENoRLXAOT%2BQe4R3C3NjlYJE5myu%2FmfsWEhtDjoqc%3D; unb=280885558; t=160b81ebbba3d0e1ebf6bdcc3767a4ec; _l_g_=Ug%3D%3D; _nk_=liminglives; cookie17=UUBYjOisWsBJ; login=true; swfstore=223484; x=__ll%3D-1%26_ato%3D0; tt=sec.taobao.com; l=AhkZMpmuQo8wKkRhz1vcQmDeqQ7zmg1X; pnm_cku822=238UW5TcyMNYQwiAiwQRHhBfEF8QXtHcklnMWc%3D%7CUm5Ockp3TntDdkt0SndKcCY%3D%7CU2xMHDJ7G2AHYg8hAS8UKQcnCVU0Uj5ZJ11zJXM%3D%7CVGhXd1llXWBZbFRhXGNdYF1nUG1PcEt2THNMd093S3BIckpkMg%3D%3D%7CVWldfS0QMAU7BCQYIAAuCiFnAF05UApBPlMQOxskClwK%7CVmhIGCUFOQI%2FAiIeJhMtDTYLMQsrFywRLAw4BTgYJB8iHz8KMQxaDA%3D%3D%7CV25Tbk5zU2xMcEl1VWtTaUlwJg%3D%3D; res=scroll%3A1583*6077-client%3A1583*794-offset%3A1583*6077-screen%3A1600*900; cna=VtDTERQLnmwCAXbyG241gYgV; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; whl=-1%260%260%260; isg=Aq6u9a7reyvkqI_MBK1s1wj3_wSwB7rt4Q5CqNh3GrFsu04VQD_CuVS7BRGs'

    #cookie = {"cookie2":"18d011caacea5cc233620bb4662dcfc1", "t":"917c68ce59c74e1ff951ce3d10f85173", "_tb_token_":"3e305a7773e73"}
    #cookie = {'pnm_cku822': '053UW5TcyMNYQwiAiwQRHhBfEF8QXtHcklnMWc%3D%7CUm5Ockt%2FRX1BdUl0SHRMdCI%3D%7CU2xMHDJ7G2AHYg8hAS8XIgwsAl4%2FWTVSLFZ4Lng%3D%7CVGhXd1llXGhSalZiXmNfY1tjVGlLf0J6RXhHe0J7Q3pDfEB9SWcx%7CVWldfS0TMwowDi4QMB4%2BBycJXwk%3D%7CVmhIGCUFOBgkHCkXNwwxDjoaJh0gHT0JNAkpFS4TLg47AD1rPQ%3D%3D%7CV25Tbk5zU2xMcEl1VWtTaUlwJg%3D%3D', 'cookie2': '107f1cda7786efd49c936682831630a0', 'isg': 'AlVVgGIIoNYQSYTX7bpqrI_iZFHP-sEgexDXBtf6FEwbLnUgn6IZNGPsjgRj', 'res': 'scroll%3A1583*6029-client%3A1583*794-offset%3A1583*6029-screen%3A1600*900', 'sm4': '310100', 'l': 'AtbWc7Qb21jdcFYTShEr6844pofYdxqx', 't': '6144bba42e39924704079cb1fb909e3c', '_m_h5_tk': '2098407e44994fb6a22a82ef41186a3a_1497519252292', 'cna': '0FrBEXmazlsCAXbyG27/LQqQ', 'cq': 'ccp%3D1', '_m_h5_tk_enc': 'fd5bab0717d458f1425740cb70270337', '_tb_token_': 'c51bb3c61eadb', '_med': 'dw:1600&dh:900&pw:1600&ph:900&ist:0'}
    #cookie = {}

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
        with open('tmall_homepage.html', 'w') as f:
            f.write(response.body)
        return self.parse_homepage(response)


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


    def parse_goods_list(self, response):
        context = response.meta['context']
        brand_name = response.meta['brand_name']
        brand_id = response.meta['brand_id']
        page_no = response.meta['page_no']

        data = unicode(response.body, errors = 'replace')
        j = json.loads(data)

        self.fout_raw.write(json.dumps({'brand':brand_id, 'cat':context['cat'], 'page_no':page_no, 'goods':j}) + "\n")

        for item in j['item']:
            goods = {} #TmallCatBrandGoodsItem()
            #goods['main_cat'] = context['main_cat']
            #goods['sub_cat'] = context['sub_cat']
            #goods['sub_cat_hotword'] = context['sub_cat_hotword']
            #goods['cat_id'] = context['cat']
            #goods['appid'] = context['appid']
            #goods['brand_id'] = brand_id

            goods['category'] = context['main_cat']['title']
            goods['subcategory'] = context['sub_cat']['title']
            goods['subcategory_hotword'] = context['sub_cat_hotword']['title']
            goods['brand_name'] = brand_name            
            goods['goods_title'] = item['title']
            goods['goods_url'] = item['url']
            goods['goods_price'] = item['price']
            goods['goods_sold'] = item['sold']
            goods['shop_name'] = item['shop_name']
            goods['shop_id'] = item['shop_id']
            goods['location'] = item['location']

            self.fout.write(json.dumps(goods) + '\n')

        total_page = j['total_page']
        total_results = j['total_results']

        if page_no < total_page:
            page_no += 1
            url = 'https://list.tmall.com/m/search_items.htm?style=list'
            url += '&cat=' + context['cat']
            url += '&brand=' + brand_id
            url += '&page_no=' + str(page_no)
            req = scrapy.Request(url = url, headers = self.hheaders, callback = self.parse_goods_list)
            req.meta['context'] = context
            req.meta['brand_name'] = brand_name
            req.meta['brand_id'] = brand_id
            req.meta['page_no'] = page_no
            yield req



