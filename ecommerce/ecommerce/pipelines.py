# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

class EcommercePipeline(object):
	def open_spider(self, spider):
		self.w = open("tmall.dat", "w")
	
	def close_spider(self, spider):
		self.w.close()
		
	def process_item(self, item, spider):
		self.w.write(json.dumps(dict(item)) + "\n")
		return item
