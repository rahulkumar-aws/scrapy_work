import os
import scrapy
from scrapy import signals
import pickle
import re

class EbookSpider(scrapy.Spider):
    name = "ebook"
    start_urls = ['http://www.ebook777.com/drawing/']
    def parse(self, response):

        ####### start from home page & follow category links 
        # for href in response.css('li.cat-item  a::attr(href)'):
        #     yield response.follow(href, self.parse_cat)

        ####### start from cat page eg. design 
        yield response.follow(response.url, self.parse_cat)

    ###### function to parse category page and follow
    def parse_cat(self, response):
        category = response.url.split('/')[3]
        for a in response.css('a.title::attr(href)'):
            yield response.follow(a, callback=self.parse_book, meta={'category': category})
        for a in response.css('a.next.page-numbers::attr(href)'):
            yield response.follow(a, callback=self.parse_cat)

    ###### function to parse book page, check if already downloaded
    def parse_book(self, response):
        category = response.meta['category']
        title = response.css('h1.title::text').extract_first()
        title = re.sub(r'\W','_',title)
        path = category +'/'+title
        download_link = response.css('span.download-links a::attr(href)').extract_first()
        if not os.path.exists(path):
            self.logger.info('[Save] %s in %s category', title, category)
            yield response.follow(download_link, callback=self.save_pdf, meta={'category': category, 'title': title, 'path': path})
        else:
            self.logger.info('[409] %s / %s ', category, title)

    ###### download the book in "category folder"
    def save_pdf(self, response):
        path = response.meta['path']
        category = response.meta['category']
        title = response.meta['title']
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(response.body)
