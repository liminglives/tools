# -*- coding: utf-8 -*-
#import ConfigParser as cfp
import scrapy
import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import urlparse

import logging
import re
import json
import pandas as pd
import requests


logger = logging.getLogger()


class TmallCatItem(scrapy.Item):
    CatId = scrapy.Field()
    CatName = scrapy.Field()
    CatLevel = scrapy.Field()
    BigBrotherCatId = scrapy.Field()
    ParentCatId = scrapy.Field()
    status = scrapy.Field()

class TmallCatSpider(CrawlSpider):
    name = 'tmallcat'
#    download_delay =2
    randomize_download_delay = True
    custom_settings = {
        'DEPTH_LIMIT':10,
        'DOWNLOAD_DELAY': 0.0001,
        'ITEM_PIPELINES':{
            'ecommerce.pipelines.DataFrameExportPipeline': 400,
         },
    }

    allowed_domains = ['tmall.com']
    start_urls = ['https://www.tmall.com/',]


    def __init__(self, conf_file=None):
        super(TmallCatSpider, self).__init__()

        today = datetime.datetime.now().strftime('%F')
        self.date = today
        self.date_set = set([today,])



    '''
    '''
    def start_requests(self):
        for start_url in self.start_urls:
            yield scrapy.Request(start_url, callback=self.parse_homepage)

    def parse_homepage(self, response):
        logger.info(response)
        json_str = response.xpath('//div[@id="J_defaultData"]/text()').extract_first()
        json_obj = json.loads(json_str)
        cat_info = json_obj['page']['100']

        cat_info_list = []
        for k, v in cat_info.items():
            if re.search('hotWordType\d+', k):
                cat_info_list.extend(v)
            else:
                pass
        df = pd.DataFrame(cat_info_list)
        df['appId'] = df['appId'].astype(str)
#        df = df.head()
        appids_str = ','.join(df['appId'])
#        appids_str = '2016031466'
#        appids_str = '2016030746'
#        appids_str = '2016031442'
        url = 'https://aldh5.tmall.com/recommend2.htm?appId=%s' %appids_str
        req = scrapy.Request(url, callback=self.parse_homepage_ids)
        req.meta['req_url'] = url
        yield req

    def parse_homepage_ids(self, response):
        logger.info(response.url)
        try:
            json_obj = json.loads(response.text)
        except:
            url = response.meta['req_url']
            req = scrapy.Request(url, callback=self.parse_homepage_ids)
            req.meta.update(response.meta)
            req.meta['change_proxy'] = True
            yield req

        for k, v in json_obj.items():
            for item in v['data']:
                url = item['action']
                title = item['title']
                parsed = urlparse.urlparse(url)
                params = urlparse.parse_qs(str(parsed.query))
                cats = params.get('cat')
                if cats is not None:
                    cat_list = cats[0].split(',')
                else:
                    cat_list = []
                keywords = params.get('q')
                if keywords is not None:
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
                    if cat == 'all':
                        continue
                    brother_url = "https://list.tmall.com/ajax/getAllBrotherCats.htm?t=0&cat=%s&sort=s&style=g&search_condition=7" %cat
                    yield scrapy.Request(brother_url, callback=self.parse_brothers, meta={'cat':cat, 'title':title, 'keyword':keyword, 'req_url':brother_url})

                if keyword is not None:
                    for cat in cat_list or ['',]:
                        #search_url = parsed._replace(path='/m'+parsed.path).geturl()
                        search_url = 'https://list.tmall.com/m/search_items.htm?page_size=1&page_no=1&cat=%s&type=p&sort=d&style=list&q=%s' %(cat, keyword or '')
                        req = scrapy.Request(search_url, callback=self.parse_search_items)
                        req.meta['req_url'] = search_url
                        yield req


    def parse_brothers(self, response):
#        logger.info(response.url)
        try:
            json_obj = json.loads(response.text)
        except:
            url = response.meta['req_url']
            req = scrapy.Request(url, callback=self.parse_brothers)
            req.meta.update(response.meta)
            req.meta['change_proxy'] = True
            yield req
        query_cat = response.meta['cat']
        title = response.meta['title']
        keyword = response.meta['keyword']
#            logger.warn('seems top level, cat:%s, title:%s, keyword:%s' %(query_cat, title, keyword))

        '''
        # title as cat name only if keyword is None
        if keyword is not None:
            title = None
        '''
        sr_list = []
        for item in json_obj:
            name = item['title']
            href = item['href']
            params = urlparse.parse_qs(urlparse.urlparse(href).query)
            cats = params.get('cat')
            if cats is not None:
                cat = cats[0]
                sr_list.append({'CatId':cat, 'CatName':name})

        sr_list.append({'CatId':query_cat, 'CatName':None})
        if len(sr_list)>0:
            df = pd.DataFrame(sr_list)
            bigbrother_catid = df['CatId'].max()
            df['BigBrotherCatId'] = bigbrother_catid
            for _, row in df.iterrows():
                Item = TmallCatItem()
                Item['CatId'] = row['CatId']
                Item['CatName'] = row['CatName']
                Item['CatLevel'] = None
                Item['BigBrotherCatId'] = row['BigBrotherCatId']
                Item['status'] = 'brothers'
                yield Item

            # get ancestors
            url = "https://list.tmall.com/m/search_items.htm?page_size=1&page_no=1&cat=%s&type=p&sort=d&style=list" %bigbrother_catid
            logger.info('search for %s' %bigbrother_catid)
            req = scrapy.Request(url, callback=self.parse_search_items)
            req.meta['req_url'] = url
            yield req

            # just to get CatName ...
            if query_cat != bigbrother_catid:
                url = "https://list.tmall.com/ajax/getAllBrotherCats.htm?t=0&cat=%s&sort=s&style=g&search_condition=7&_=_" %bigbrother_catid
                req = scrapy.Request(url, callback=self.parse_brothers, meta={'cat':bigbrother_catid, 'title':None, 'keyword':None})
                req.meta['req_url'] = url
                yield req


    def parse_search_items(self, response):
#        logger.info(response.url)
        try:
            json_obj = json.loads(response.text)
        except:
            url = response.meta['req_url']
            req = scrapy.Request(url, callback=self.parse_search_items)
            req.meta.update(response.meta)
            req.meta['change_proxy'] = True
            yield req
        cat_infos = json_obj['cat']
        selected_cat_path = cat_infos['selected_cat_path']
        sub_cat_list = cat_infos['sub_cat_list']

        # find ancesters and set level
        level = 1
        parent_catid = None
        for cat_info in selected_cat_path:
            cat_id = str(cat_info['cat_id'])
            cat_name = cat_info['cat_name']
            Item = TmallCatItem()
            Item['CatId'] = cat_id
            Item['CatName'] = cat_name
            Item['CatLevel'] = level
            Item['BigBrotherCatId'] = cat_id
            Item['ParentCatId'] = parent_catid
            Item['status'] = 'ancenstor'
            yield Item

            level += 1
            parent_catid = cat_id


        # extend cats if possible
        for sub_cat in sub_cat_list:
            cat = str(sub_cat['cat_id'])
            title = sub_cat['cat_name']
            keyword = None
            url = "https://list.tmall.com/ajax/getAllBrotherCats.htm?t=0&cat=%s&sort=s&style=g&search_condition=7" %cat
            yield scrapy.Request(url, callback=self.parse_brothers, meta={'cat':cat, 'title':title, 'keyword':keyword})



