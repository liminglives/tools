#-*-coding: utf-8 -*-
import json
import csv

def parse():
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

def parse2():
    goods_dict = {}
    with open('tmall_goods_list_2017-10-16_1508146029.csv') as f:
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
                    #print row
                    continue
            else:
                sold = int(sold)
            if k in goods_dict:
                goods = goods_dict[k]
                goods['SalesUnit'] += sold
                goods['SalesValue'] += sold * price
            else:
                goods = {}
                goods['BrandId'] = row['BrandId']
                goods['BrandName'] = row['BrandName']
                #goods['Brand'] = row['Brand']
                #goods['Name'] = brandinf['Name']
                goods['ProductName'] = row['ProductName']
                goods['BloombergTicker'] = row['BloombergTicker']
                goods['CatId'] = row['CatId']
                goods['CatName'] = row['CatName']
                goods['SalesUnit'] = sold
                goods['SalesValue'] = sold * price
                goods_dict[k] = goods

    with open('goods_checked_20171016_pc.csv', 'w') as f:
        headers = ['BrandId', "BrandName", "ProductName", "BloombergTicker", 'CatId', 'CatName', 'SalesUnit', 'SalesValue']
        c = csv.DictWriter(f, fieldnames = headers)
        c.writeheader()
        for k in goods_dict:
            c.writerow(goods_dict[k])


    pass

def parse3():
    goods_dict = {}
    fin = 'tmall_goods_list_total_2017-10-19_1508376247_all.csv'
    with open(fin) as f:
        c = csv.DictReader(f)
        sold_wan_unit = '万'
        for row in c:
            k = str(row['BrandId'])+'_'+ str(row['CatId'])
            sold = (row['Sold'])
            if not sold.isdigit():
                if sold_wan_unit in sold:
                    n = sold[:len(sold) - len(sold_wan_unit)]
                    sold = float(n)
                    sold = int(sold * 10000)
                    sold += 500
                else:
                    #print row
                    continue
            else:
                sold = int(sold)
            total_sold = (row['TotalSoldQuantity'])
            if not total_sold.isdigit():
                if sold_wan_unit in total_sold:
                    n = total_sold[:len(total_sold) - len(sold_wan_unit)]
                    total_sold = float(n)
                    total_sold = int(total_sold * 10000)
                    total_sold += 500
                else:
                    #print row
                    continue
            else:
                total_sold = int(total_sold)

            if k in goods_dict:
                goods = goods_dict[k]
                goods['SalesUnit'] += sold
                goods['TotalSalesUnit'] += total_sold
            else:
                goods = {}
                goods['BrandId'] = row['BrandId']
                goods['BrandName'] = row['BrandName']
                #goods['Brand'] = row['Brand']
                #goods['Name'] = brandinf['Name']
                goods['CatId'] = row['CatId']
                goods['CatName'] = row['CatName']
                goods['SalesUnit'] = sold
                goods['TotalSalesUnit'] = total_sold
                goods_dict[k] = goods

    with open(fin+'.stat.csv', 'w') as f:
        headers = ['BrandId', "BrandName", 'CatId', 'CatName', 'SalesUnit', 'TotalSalesUnit']
        c = csv.DictWriter(f, fieldnames = headers)
        c.writeheader()
        for k in goods_dict:
            c.writerow(goods_dict[k])



if __name__ == "__main__":
    parse3()
