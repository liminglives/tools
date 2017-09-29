# -*- coding: utf-8 -*-
#import ConfigParser as cfp
import scrapy
import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import urlparse

from scrapy.shell import inspect_response
import logging
import re
import json
import pandas as pd
import requests


logger = logging.getLogger()


class TmallBrandItem(scrapy.Item):
    CatId = scrapy.Field()
    CatName = scrapy.Field()
    BrandId = scrapy.Field()
    BrandName = scrapy.Field()

class TmallBrandSpider(CrawlSpider):
    name = 'tmallbrand'
#    download_delay =2
    randomize_download_delay = True
    custom_settings = {
        'DEPTH_LIMIT':5,
        'DOWNLOAD_DELAY': 0.002,
        'ITEM_PIPELINES':{
            'ecommerce.pipelines.DataFrameExportPipeline': 400,
         },
    }

    allowed_domains = ['tmall.com']
    start_urls = ['http://www.tmall.com',]

    '''
    rules = (
#        Rule(LinkExtractor(allow=(), restrict_xpaths=('//div[@class="product"]')), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@class="ui-page-next"][contains(text(), ">>")]')), callback='parse_item', follow=True),
    )
    '''

    def __init__(self, conf_file=None):
        super(TmallBrandSpider, self).__init__()

        today = datetime.datetime.now().strftime('%F')
        self.date = today
        self.date_set = set([today,])

        self.home_url = 'http://list.tmall.com/search_product.htm'
        self.df = pd.read_csv('tmallcat_2017-09-25_1506332018.csv', encoding='utf8', dtype={'CatId':str})
        self.df = self.df[self.df['CatLevel']==2]
        #df = df.head()

    '''
    '''
    def start_requests(self):
        for _, row in self.df.iterrows():
            cat_id = row['CatId']
            cat_name = row['CatName']
            url = 'https://list.tmall.com/ajax/allBrandShowForGaiBan.htm?t=0&cat=%s&sort=s&style=g&search_condition=2&from=sn_1_cat-qp' %cat_id
            logger.info('start request CatId:%s, CatName:%s' %(cat_id, cat_name))
            yield scrapy.Request(url, callback=self.parse_brand, meta={'cat_name':cat_name, 'cat_id': cat_id})

    def parse_brand(self, response):
#        logger.info(response)
        json_str = response.text
        try:
            json_obj = json.loads(json_str)
        except Exception as e:
            logger.warn("find escape character, replaced by '/' on %s" %response.url)
            json_obj = json.loads(json_str.replace('\\', '/'))

        for item in json_obj:
            brand_name = item['title']
            href = item['href']

            params = urlparse.parse_qs(str(urlparse.urlparse(href).query))
            cat_id = response.meta['cat_id']
            cat_name = response.meta['cat_name']
            brand_id = params['brand'][0]

            Item = TmallBrandItem()
            Item['CatId'] = cat_id
            Item['CatName'] = cat_name
            Item['BrandId'] = brand_id
            Item['BrandName'] = brand_name
            yield Item


    def parse_homepage_ids(self, response):
#        logger.info(response.url)
        json_obj = json.loads(response.text)
        for k, v in json_obj.items():
            for item in v['data']:
                url = item['action']
                title = item['title']
                params = urlparse.parse_qs(str(urlparse.urlparse(url).query))
                cats = params.get('cat')
                if cats is not None:
                    cat_list = cats[0].split(',')
                else:
                    cat_list = []
                keywords = params.get('q')
                if keywords is not None:
#                    inspect_response(response, self)
                    try:
                        keyword = keywords[0].decode('gbk')
                    except Exception as e:
                        logger.exception(e)
                        logger.error(keywords)
                        keyword = keywords[0].decode('utf8')
                        logger.error(keyword)

                else:
                    keyword = None

                for cat in cat_list:
#                    brothers_df = self.get_all_brothers(cat, title, keyword)

                    url = "https://list.tmall.com/ajax/getAllBrotherCats.htm?t=0&cat=%s&sort=s&style=g&search_condition=7" %cat
#                    url = 'https://list.tmall.com/ajax/getAllBrotherCats.htm?t=0&cat=56232008&sort=s&style=g&search_condition=7'
                    yield scrapy.Request(url, callback=self.parse_brothers, meta={'cat':cat, 'title':title, 'keyword':keyword}, dont_filter=True)

    def parse_brothers(self, response):
    #    url = "https://list.tmall.com/ajax/getAllBrotherCats.htm?t=0&cat=%s&sort=s&style=g&search_condition=7" %query_cat
    #    rsp = requests.get(url)
#        inspect_response(response, self)
        logger.info(response.url)
        json_obj = json.loads(response.text)
        query_cat = response.meta['cat']
        title = response.meta['title']
        keyword = response.meta['keyword']
        level = None
        if len(json_obj) == 0:
            level = 1
            if keyword is not None:
                logger.warn('seams level 1 without name, cat:%s, title:%s, keyword:%s' %(query_cat, title, keyword))
                title = None
                #return pd.DataFrame()
            else:
                logger.error(response.url)
                logger.warn('seams level 1 with name,cat:%s, title:%s, keyword:%s' %(query_cat, title, keyword))

        if keyword is None:
            query_name = title
        else:
            # title is not credible
            query_name = None
        sr_list = []
        for item in json_obj:
            name = item['title']
            href = item['href']
            params = urlparse.parse_qs(urlparse.urlparse(href).query)
            cats = params.get('cat')
            if cats is not None:
                cat = cats[0]
                if cat == 'all':
                    print response.url
                    print t
                sr_list.append({'CatId':cat, 'CatName':name})
        sr_list.append({'CatId':query_cat, 'CatName':None, 'Title':query_name})
        if len(sr_list)>0:
            df = pd.DataFrame(sr_list)
            bigbrother_catid = df['CatId'].max()
            df['BigBrotherCatId'] = bigbrother_catid
            df['CatLevel'] = level
            for _, row in df.iterrows():
                Item = TmallCatItem()
                Item['CatId'] = row['CatId']
                Item['CatName'] = row['CatName']
                Item['CatLevel'] = row['CatLevel']
                Item['BigBrotherCatId'] = row['BigBrotherCatId']
                yield Item

            # get ancestor catid
            if level != 1 or True:
                url = "https://list.tmall.com/m/search_items.htm?page_size=1&page_no=1&type=p&cat=%s&style=list" %bigbrother_catid
                yield scrapy.Request(url, callback=self.parse_ancestor)

            if query_cat != bigbrother_catid:
                url = "https://list.tmall.com/ajax/getAllBrotherCats.htm?t=0&cat=%s&sort=s&style=g&search_condition=7" %bigbrother_catid
#                url = 'https://list.tmall.com/ajax/getAllBrotherCats.htm?t=0&cat=56232008&sort=s&style=g&search_condition=7'
                logger.warn(url)
                yield scrapy.Request(url, callback=self.parse_brothers, meta={'cat':bigbrother_catid, 'title':None, 'keyword':None})

#        else:
#            return

    def parse_ancestor(self, response):
        logger.info(response.url)
        json_obj = json.loads(response.text)
        cat_infos = json_obj['cat']['selected_cat_path']
        level = 1
        parent_catid = None
        for cat_info in cat_infos:
            cat_id = str(cat_info['cat_id'])
            cat_name = cat_info['cat_name']
            Item = TmallCatItem()
            Item['CatId'] = cat_id
            Item['CatName'] = cat_name
            Item['CatLevel'] = level
            Item['BigBrotherCatId'] = None
            Item['ParentCatId'] = parent_catid
            yield Item

            level += 1
            parent_catid = cat_id


    '''
    def parse(self, response):
        logger.fatal(response)
        logger.fatal('')
        return super(TmallSpider, self).parse(response)
    '''

    def parse_item(self, response):
        keyword = urlparse.parse_qs(response.url)['q'][0].decode('gbk')
        '''
        from scrapy.shell import inspect_response
        inspect_response(response, self)
        '''
        logger.fatal(response.url)
        logger.fatal('')
        product_list = response.xpath('//*[@id="J_ItemList"]/div')
        for product in product_list:
            item = TmallItem()
            try:
                item['Date'] = self.date
                item['Keyword'] = keyword
                item['DataId'] = product.xpath('@data-id').extract()[0]
                item['Price'] = product.xpath('div/p[@class="productPrice"]/em/@title').extract()[0]
                item['Volume'] = product.xpath('div/p[@class="productStatus"]/span/em/text()').extract()[0]
                #print  item
                yield item
            except Exception as e:
                logger.exception(e)


        logger.debug(response.url)

        '''
        from scrapy.shell import inspect_response
        inspect_response(response, self)
        '''
