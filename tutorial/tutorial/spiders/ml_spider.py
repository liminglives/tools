import scrapy
import logging

class BaiduIndexSpider(scrapy.Spider):
    name = "index"
    allowed_domains = ["baidu.com"]
    start_urls = [
        "http://index.baidu.com/?tpl=trend&word=auto"
    ]
    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, sdch",
        "Accept-Language":"zh-CN,zh;q=0.8",
        "Connection":"keep-alive",
        #"Cookie":"BDUSS=EEwVmMtVHZxdzdCQ1N4dkVDOHA3SjNmSEdiSFdtYlJ5aTlleGpCYzRIdzdRbDlaSVFBQUFBJCQAAAAAAAAAAAEAAABISzYMbGltaW5nbGl2ZXMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADu1N1k7tTdZV; CHKFORREG=107eeddb9dc0febc691c4cc47a475066; BAIDUID=9D46A9BCFA7BAE2853589FA14BFE0D2E:FG=1; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1496823129; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1496823129; searchtips=1",
        "Host":"index.baidu.com",
        "Referer":"http://index.baidu.com/",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    cookie = {
        #"BDUSS":"EEwVmMtVHZxdzdCQ1N4dkVDOHA3SjNmSEdiSFdtYlJ5aTlleGpCYzRIdzdRbDlaSVFBQUFBJCQAAAAAAAAAAAEAAABISzYMbGltaW5nbGl2ZXMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADu1N1k7tTdZV",
        "BDUSS":"1QxeXUwNnNoLTQtZ0RaN0xMcn5HRXVRTVZvSnJPNn5mandQb1UxbEhPOGZmMkJaSVFBQUFBJCQAAAAAAAAAAAEAAABISzYMbGltaW5nbGl2ZXMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB~yOFkf8jhZb",
        "CHKFORREG":"107eeddb9dc0febc691c4cc47a475066",
        #"BAIDUID":"9D46A9BCFA7BAE2853589FA14BFE0D2E:FG=1",
        "BAIDUID":"7260E2C56BF56A9472396E34CEDE7D23:FG=1",
        "Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc":"1496823129",
        "Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc":"1496823129",
        "searchtips":"1",

    }

    def get_item(self, line, key, end_str=";"):
        ret = ""
        index = line.find(key)
        start = index + len(key)
        if index != -1:
            end = line[start:].find(end_str)
            ret = line[start : start + end]
        return ret

    def get_baidu_login_cookie(self):
        baiduid = ""
        bduss = ""
        with open("baidu_cookies.dat", "r") as f:
            for line in f:
                ret = self.get_item(line, "BAIDUID=", ";")
                if ret != "":
                    baiduid = ret
                ret = self.get_item(line, "BDUSS=", ";")
                if ret != "":
                    bduss = ret

        return baiduid, bduss


    def start_requests(self):
        baiduid, bduss = self.get_baidu_login_cookie()
        self.cookie["BAIDUID"] = baiduid
        self.cookie["BDUSS"] = bduss
        logging.error("bid:%s, bduss:%s", baiduid, bduss)
        yield scrapy.Request(
            url = self.start_urls[0],
            headers = self.headers,
            cookies = self.cookie,
            callback = self.parse)

    def parse(self, response):
        filename = response.url.split("/")[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)