import scrapy

class DmozSpider(scrapy.Spider):
    name = "dmoz"
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0",
        "Upgrade-Insecure-Requests":"1",
    }
    allowed_domains = ["sogou.com", "tmall.com"]
    start_urls = [
        #"https://123.sogou.com/",
        "https://www.tmall.com"
    ]

    def start_requests(self):
        yield scrapy.Request(
            url = self.start_urls[0],
            headers = self.headers,
            callback = self.parse)

    def parse(self, response):
        filename = response.url.split("/")[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)