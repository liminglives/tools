import csv
import copy

brand_spider_dict = {}

with open('cat_brand.csv') as f:
    c = csv.DictReader(f)
    for row in c:
        brand_name = row['BrandName'].lower()
        if brand_name in brand_spider_dict:
            if row['BrandId'] != brand_spider_dict[brand_name]['BrandId']:
                print 'duplicate', brand_name, row['BrandId']
        else:
            info = {}
            info['BrandName'] = row['BrandName']
            info['BrandId'] = row['BrandId']
            brand_spider_dict[brand_name] = info
            idx = brand_name.find('/')
            if idx != -1:
                subbrands = brand_name.split('/')
                for b in subbrands:
                    brand_spider_dict[b] = info


brand_match_dict = {}
brand_part_match_dict = {}
brand_unmatch_dict = {}
brand_all_dict = {}
header = None

with open('brand_all.csv') as f:
    c = csv.DictReader(f)
    header = c.fieldnames
    for row in c:
        brand_name = row['Brand'].lower()
        subbrands = brand_name.split('/')
        hit = False
        if brand_name in brand_spider_dict:
            info = brand_spider_dict[brand_name]
            info['Key'] = brand_name
            info['Brand'] = row['Brand']
            info['FinancialType'] = 'Stock'#row['Category']
            info['ProductName'] = row['ProductName']
            info['BloombergTicker'] = row['Bloomberg Ticker']
            brand_match_dict[brand_name] = info
            hit = True
        elif len(subbrands) > 0:
            for b in subbrands:
                if b in brand_spider_dict:
                    info = brand_spider_dict[b]
                    info['Key'] = b
                    info['Brand'] = row['Brand']
                    info['FinancialType'] = 'Stock'#row['Category']
                    info['ProductName'] = row['ProductName']
                    info['BloombergTicker'] = row['Bloomberg Ticker']
                    #brand_match_dict[b] = info
                    brand_part_match_dict[b] = info
                    hit = True
                    print b
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
    for brand in brand_match_dict:
        c.writerow(brand_match_dict[brand])

with open('brand_part_match.csv', 'w') as f:
    headers = ['Key', 'BrandId', 'BrandName', 'Brand', "FinancialType", 'ProductName', "BloombergTicker"]
    c = csv.DictWriter(f, fieldnames = headers)
    c.writeheader()
    for brand in brand_part_match_dict:
        c.writerow(brand_match_dict[brand])


with open('brand_unmatch.csv', 'w') as f:
    c = csv.DictWriter(f, fieldnames = header)
    c.writeheader()
    for brand in brand_unmatch_dict:
        c.writerow(brand_unmatch_dict[brand])







