# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import json
import pandas as pd
import numpy as np
import datetime
import re
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter

logger = logging.getLogger()


class EcommercePipeline(object):
    def open_spider(self, spider):
        self.w = open("tmall.dat", "w")

    def close_spider(self, spider):
        self.w.close()

    def process_item(self, item, spider):
        self.w.write(json.dumps(dict(item)) + "\n")
        return item

class DataFrameExportPipeline(object):
    def open_spider(self, spider):
        logger.debug( 'in open_spider')
        self.df_list = []
        now = datetime.datetime.now().strftime('%s')

        begin_date = min(spider.date_set)
        end_date = max(spider.date_set)
        if begin_date == end_date:
            self.filepath = '%s_%s_%s' %(spider.name, begin_date, now)
        else:
            self.filepath = '%s_%s_%s_%s' %(spider.name, begin_date, end_date, now)
        try:
            self.filepath = './' + self.filepath
        except Exception as e:
            logger.error(e)

    def process_item(self, item, spider):
        logger.debug( 'in process_item')
        self.df_list.append(item)
        return item

    def merge_goods(self, spider):
        try:
            goods_dict = spider.merge_goods(self.df_list)
            df = pd.DataFrame(goods_dict.values())
            df = df.drop_duplicates()
            df.to_csv(self.filepath + '_merged.csv', index=False, encoding='utf8', na_rep='NaN')
        except:
            pass

    def close_spider(self, spider):
        logger.debug('in close_spider')
        if spider.name == 'tmall_goods_list':
            self.merge_goods(spider)
        df = pd.DataFrame(self.df_list)
        df = df.drop_duplicates()
        df.to_csv(self.filepath + '.csv', index=False, encoding='utf8', na_rep='NaN')
        logger.debug(self.filepath)

class MultiDataFrameExportPipeline(object):
    def open_spider(self, spider):
        logger.debug( 'in open_spider')
        self.df_dict = {}
        now = datetime.datetime.now().strftime('%s')
        self.spider_name = spider.name

        begin_date = min(spider.date_set)
        end_date = max(spider.date_set)
        if begin_date == end_date:
            self.date_str = '%s_%s.csv' %(begin_date, now)
        else:
            self.date_str = '%s_%s_%s.csv' %(begin_date, end_date, now)

        #try:
        #    self.filepath = './' + self.filepath
        #except Exception as e:
        #    logger.error(e)

    def process_item(self, item, spider):
        logger.debug( 'in process_item')
        item_name = item.__class__.__name__
        if item_name not in self.df_dict:
            self.df_dict[item_name] = []
        self.df_dict[item_name].append(item)
        return item

    def close_spider(self, spider):
        logger.debug('in close_spider')
        for item_name in self.df_dict:
            df = pd.DataFrame(self.df_dict[item_name])
            df = df.drop_duplicates()
            path = "%s_%s_%s" % (self.spider_name, item_name, self.date_str)
            df.to_csv(path , index=False, encoding='utf8', na_rep='NaN')


