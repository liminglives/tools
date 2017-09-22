#-*-coding: utf-8 -*-
import json
import csv

brand_cat_dict = {}
goods_dict = {}
brand_info_dict = {}

with open('cat_brand.csv') as f:
    c = csv.DictReader(f)
    for row in c:
        k = str(row['BrandId'])+'_'+ str(row['CatId'])
        if k in brand_cat_dict:
            print k, 'existed'
            continue
        brand_cat_dict[k] = row

with open('brand_code.csv') as f:
    c = csv.DictReader(f)
    for row in c:
        brand_info_dict[row['BrandId']] = row

with open('goods.data') as f:
    c = csv.DictReader(f)
    sold_wan_unit = '万'
    for row in c:
        k = str(row['BrandId'])+'_'+ str(row['CatId'])
        sold = (row['Sold'])
        price = float(row['Price'])
        if not sold.isdigit():
            if sold_wan_unit in sold:
                n = sold[:len(sold) - len(sold_wan_unit)]
                sold = float(n)
                sold = int(sold * 10000)
                sold += 500
            else:
                print row
                continue
        else:
            sold = int(sold)
        if k in goods_dict:
            goods = goods_dict[k]
            goods['SalesUnit'] += sold
            goods['SalesValue'] += sold * price
        else:
            goods = {}
            brandinf = brand_info_dict[row['BrandId']]
            goods['BrandId'] = brandinf['BrandId']
            goods['BrandName'] = brandinf['BrandName']
            goods['Brand'] = brandinf['Brand']
            goods['Name'] = brandinf['Name']
            goods['ProductName'] = brandinf['ProductName']
            goods['Bloomberg Ticker'] = brandinf['Bloomberg Ticker']
            goods['Category2Id'] = row['CatId']
            goods['Category2Name'] = brand_cat_dict[k]['CatName']
            goods['SalesUnit'] = sold
            goods['SalesValue'] = sold * price
            goods_dict[k] = goods

with open('stock_goods.csv', 'w') as f:
    headers = ['BrandId', "BrandName", "Brand", "Name", "ProductName", "Bloomberg Ticker", 'Category2Id', 'Category2Name', 'SalesUnit', 'SalesValue']
    c = csv.DictWriter(f, fieldnames = headers)
    c.writeheader()
    for k in goods_dict:
        c.writerow(goods_dict[k])
