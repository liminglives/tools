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
            self.filepath = '%s_%s_%s.csv' %(spider.name, begin_date, now)
        else:
            self.filepath = '%s_%s_%s_%s.csv' %(spider.name, begin_date, end_date, now)
        try:
            self.filepath = './' + self.filepath
        except Exception as e:
            logger.error(e)

    def process_item(self, item, spider):
        logger.debug( 'in process_item')
        self.df_list.append(item)
        return item

    def close_spider(self, spider):
        logger.debug('in close_spider')
        df = pd.DataFrame(self.df_list)
        df = df.drop_duplicates()
        df.to_csv(self.filepath, index=False, encoding='utf8', na_rep='NaN')
        logger.debug(self.filepath)


