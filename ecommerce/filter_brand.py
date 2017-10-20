import csv
import copy

brand_spider_dict = {}
brandid_spider_dict = {}

with open('cat_brand.csv') as f:
    c = csv.DictReader(f)
    for row in c:
        brand_name = row['BrandName'].strip().lower()
        brand_id = row['BrandId']
        if brand_id not in brandid_spider_dict:
            brandid_spider_dict[brand_id] = brand_name

        if brand_name in brand_spider_dict:
            brand_spider_dict[brand_name].add(brand_id)
            #if row['BrandId'] != brand_spider_dict[brand_name]['BrandId']:
            #    print 'duplicate', brand_name, row['BrandId']
        else:
            info = set()
            info.add(brand_id)
            brand_spider_dict[brand_name] = info
            idx = brand_name.find('/')
            if idx != -1:
                subbrands = brand_name.split('/')
                for b in subbrands:
                    b = b.strip()
                    if b in brand_spider_dict:
                        brand_spider_dict[b].add(brand_id)
                    else:
                        info1 = set()
                        info1.add(brand_id)
                        brand_spider_dict[b] = info1


brand_match_list = []
brand_part_match_list = []
brand_unmatch_dict = {}
brand_all_dict = {}
header = None
other_brand_set = set()

with open('brand_goods_all.csv') as f:
    c = csv.DictReader(f)
    header = c.fieldnames
    for row in c:
        brand_name = row['Brand'].strip().lower()
        if brand_name in other_brand_set:
            continue
        other_brand_set.add(brand_name)
        subbrands = brand_name.split('/')
        hit = False
        brand_all_dict[brand_name] = row
        if brand_name in brand_spider_dict:
            print  brand_spider_dict[brand_name]
            for brandid in brand_spider_dict[brand_name]:
                info = {}
                info['Key'] = brand_name
                info['BrandId'] = brandid
                info['BrandName'] = brandid_spider_dict[brandid]
                info['Brand'] = row['Brand']
                info['FinancialType'] = 'Stock'#row['Category']
                info['ProductName'] = row['ProductName']
                info['BloombergTicker'] = row['Bloomberg Ticker']
                brand_match_list.append(info)
            hit = True
        elif len(subbrands) > 0:
            for b in subbrands:
                b = b.strip()
                if b in brand_spider_dict:
                    for brandid in brand_spider_dict[b]:
                        info = {}
                        info['Key'] = b
                        info['BrandId'] = brandid
                        info['BrandName'] = brandid_spider_dict[brandid]
                        info['Brand'] = row['Brand']
                        info['FinancialType'] = 'Stock'#row['Category']
                        info['ProductName'] = row['ProductName']
                        info['BloombergTicker'] = row['Bloomberg Ticker']
                        #brand_match_dict[b] = info
                        brand_part_match_list.append(info)
                    hit = True
        if not hit:
            brand_unmatch_dict[brand_name] = row


#with open('cat_brand.csv') as f:
#    c = csv.DictReader(f)
#    for row in c:
#        brand_name = row['BrandName']
#        if brand_name in brand_all_dict:
#            info = brand_all_dict[brand_name]
#            info.update(row)
#            info['Key'] = brand_name
#            brand_match_dict[brand_name] = info
#        else:
#            subbrands = brand_name.split('/')
#            if len(subbrands) > 0:
#                for b in subbrands:
#                    if b in brand_all_dict:
#                        info = brand_all_dict[b]
#                        info.update(row)
#                        info['Key'] = b
#                        brand_match_dict[b] = info
#                        print b, row

with open('brand_match.csv', 'w') as f:
    headers = ['Key', 'BrandId', 'BrandName', 'Brand', "FinancialType", 'ProductName', "BloombergTicker"]
    c = csv.DictWriter(f, fieldnames = headers)
    c.writeheader()
    for brand in brand_match_list:
        c.writerow(brand)

with open('brand_part_match.csv', 'w') as f:
    headers = ['Key', 'BrandId', 'BrandName', 'Brand', "FinancialType", 'ProductName', "BloombergTicker"]
    c = csv.DictWriter(f, fieldnames = headers)
    c.writeheader()
    for brand in brand_part_match_list:
        c.writerow(brand)


with open('brand_unmatch.csv', 'w') as f:
    c = csv.DictWriter(f, fieldnames = header)
    c.writeheader()
    for brand in brand_unmatch_dict:
        c.writerow(brand_unmatch_dict[brand])

with open('brand_all.csv', 'w') as f:
    c = csv.DictWriter(f, fieldnames = header)
    c.writeheader()
    for brand in brand_all_dict:
        c.writerow(brand_all_dict[brand])







