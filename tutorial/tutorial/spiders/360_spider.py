import scrapy
import logging

class QH360Spider(scrapy.Spider):
    name = "360"
    allowed_domains = ["so.com"]
    start_urls = [
        #"http://trends.so.com/result/trend?keywords=auto&time=30",
        "http://www.so.com/?src=so.com"
    ]
    cookie_file = "360_cookie.dat"

    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, sdch",
        "Accept-Language":"zh-CN,zh;q=0.8",
        "Cache-Control":"max-age=0",
        "Connection":"keep-alive",
        "Host":"www.so.com",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    cookie = {
        "test_cookie_enable":"null",
        #"Q":"u%3D360H2907928383%26n%3D%26le%3D%26m%3DZGt4WGWOWGWOWGWOWGWOWGWOAwR5%26qid%3D2907928383%26im%3D1_t00df551a583a87f4e9%26src%3Dpcw_so%26t%3D1aaaa",
        "Q":"u%3D360H2907928383%26n%3D%26le%3D%26m%3DZGt4WGWOWGWOWGWOWGWOWGWOAwR5%26qid%3D2907928383%26im%3D1_t00df551a583a87f4e9%26src%3Dpcw_cloud%26t%3D1",
        #"T":"s%3D6b1a0f25c6f1b222a993b7ba753fe5ad%26t%3D1497252012%26lm%3D%26lf%3D2%26sk%3D9636954ffe4ba6bcc84282b66dc4f183%26mt%3D1497252012%26rc%3D%26v%3D2.0%26a%3D1",
        "T":"s%3D12041f83f4aac1bb047e829ee3ee9939%26t%3D1497251620%26lm%3D%26lf%3D2%26sk%3De309a12f2c717ea2d1cc4faa40682708%26mt%3D1497251620%26rc%3D%26v%3D2.0%26a%3D0",
        "__huid":"11ulgcnsw3qrbjx5DabKDoYDJC1ZR65FVSRdZUm3rhXGw%3D",
        "_S":"4b32f0279b407d545f20bee0f931b8be",
        "__bn":"OBS%7BOxSnBwO%24%2FBVKOQFw%3CO%3EVtRV3%7BqFLq%2C%3C%2BU%7Bp.d%28qonX%294QT1pDzgz%7DYTGQ%40%3EJ%3FMVf%2C%5E0%3F%7C%2BsQlSeR%23lA8gZW%2C2Ep9Bu%25dHerk",
        "monitor_count":"1",
        "__guid":"210905680.4043394721534833700.1497252028526.0315",
        "__gid":"210905680.823467281.1497252028526.1497252028526.1",
        "__sid":"210905680.60643784992561560.1497252028527.8586"

    }

    def get_item(self, line, key, end_str=";"):
        ret = ""
        index = line.find(key)
        start = index + len(key)
        if index != -1:
            end = line[start:].find(end_str)
            ret = line[start : start + end]
        return ret

    def get_360_login_cookie(self):
        cookie_T = ""
        cookie_Q = ""
        with open(self.cookie_file, "r") as f:
            for line in f:
                ret = self.get_item(line, 'T="', '"')
                if ret != "":
                    cookie_T = ret
                ret = self.get_item(line, 'Q="', '"')
                if ret != "":
                    cookie_Q = ret

        return cookie_T, cookie_Q


    def start_requests(self):
        cookie_T, cookie_Q = self.get_360_login_cookie()
        self.cookie["T"] = cookie_T
        self.cookie["Q"] = cookie_Q
        logging.error("T:%s, Q:%s", cookie_T, cookie_Q)
        yield scrapy.Request(
            url = self.start_urls[0],
            headers = self.headers,
            cookies = self.cookie,
            callback = self.parse)

    def parse(self, response):
        #filename = response.url.split("/")[-2] + '.html'
        filename = '360.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
