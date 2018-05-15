import os
import scrapy
from scrapy import signals
import pickle
import re

class EbookSpider(scrapy.Spider):
    name = "etisalat"
    start_urls = ['http://support.etisalat.ae/en/index.jsp']
    def parse(self, response):
        ####### start from home page & follow category links 
        for href in response.css('.prodotto a::attr(href)'):
            yield response.follow(href, self.parse_cat)

    ###### function to parse category page and follow
    def parse_cat(self, response):
        category = response.url.split('/')[-1].split('.')[0]
        for href in response.css('.grid__item > a::attr(href)'):
            yield response.follow(href, callback=self.parse_subcat, meta={'category': category})

    def parse_subcat(self, response):
        sub_category = response.url.split('/')[-1].split('.')[0]
        # heading response.css('.title-main-collapse')
        for heading in response.css('.main-collapse'):
            for question in heading.css('.title-collapse'):
                x = question.xpath('following-sibling::div[1]/p/text()').extract() 
                if not x:
                    x = question.xpath('following-sibling::div[1]/text()').extract()
                yield {
                    'question': question.xpath('./text()').extract()[0],
                    'answer': x,
                    'cat': response.meta['category'],
                    'sub_cat': sub_category
                }

    # ###### function to parse book page, check if already downloaded
    # def parse_question(self, response):
    #     category = response.meta['category']
    #     title = response.css('h1.title::text').extract_first()
    #     title = re.sub(r'\W','_',title)
    #     path = category +'/'+title
    #     download_link = response.css('span.download-links a::attr(href)').extract_first()
    #     if not os.path.exists(path):
    #         self.logger.info('[Save] %s in %s category', title, category)
    #         yield response.follow(download_link, callback=self.save_pdf, meta={'category': category, 'title': title, 'path': path})
    #     else:
    #         self.logger.info('[409] %s / %s ', category, title)

    # ###### download the book in "category folder"
    # def save_pdf(self, response):
    #     path = response.meta['path']
    #     category = response.meta['category']
    #     title = response.meta['title']
    #     os.makedirs(os.path.dirname(path), exist_ok=True)
    #     with open(path, 'wb') as f:
    #         f.write(response.body)
