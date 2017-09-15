# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EcommerceItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    data_id = scrapy.Field()
    price = scrapy.Field()
    sale_amount = scrapy.Field()
    shop = scrapy.Field()

class TmallCategory(scrapy.Item):
    # define the fields for your item here like:
    main_cat = scrapy.Field()
    sub_cat = scrapy.Field()
    subcat_hotword = scrapy.Field()
    subcat_hotword_url = scrapy.Field()
    hotword_brand = scrapy.Field()

class TmallCatBrandItem(scrapy.Item):
    # define the fields for your item here like:
    main_cat = scrapy.Field()
    sub_cat = scrapy.Field()
    appid = scrapy.Field() # sub_cat id
    sub_cat_hotword = scrapy.Field()
    cat_id = scrapy.Field() # sub cat hotword id
    brands = scrapy.Field()

class TmallCatBrandGoodsItem(scrapy.Item):
    # define the fields for your item here like:
    main_cat = scrapy.Field()
    sub_cat = scrapy.Field()
    appid = scrapy.Field() # sub_cat id
    sub_cat_hotword = scrapy.Field()
    cat_id = scrapy.Field() # sub cat hotword id
    brand_name = scrapy.Field()
    brand_id = scrapy.Field()
    goods_title = scrapy.Field()
    goods_url = scrapy.Field()
    goods_price = scrapy.Field()
    goods_sold = scrapy.Field()
    shop_name = scrapy.Field()
    shop_id = scrapy.Field()
    location = scrapy.Field()
