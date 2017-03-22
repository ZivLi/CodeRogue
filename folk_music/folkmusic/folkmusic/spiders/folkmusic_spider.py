# coding: utf-8
import scrapy

class FolkMusicSpider(scrapy.Spider):
    name = "folkmusic"
    allowed_domains = ["folkmusic.org"]
    start_urls = [
        "http://www.baidu.com",
    ]

    def parse(self, response):
        filename = response.url.split('/')[-2]
        with open(filename, 'wb') as f:
            f.write(response.body)
