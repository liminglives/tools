import scrapy

class IPSpider(scrapy.Spider):
    name = "ip"
    allowed_domains = ["dmoz.org", "baidu.com"]
    start_urls = [
        "http://www.kuaidaili.com/free",
    ]

    def parse(self, response):
        filename = response.url.split("/")[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)