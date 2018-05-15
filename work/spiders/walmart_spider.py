import os
import scrapy
from scrapy import signals
import pickle
import re

class WalmartSpider(scrapy.Spider):
    name = "walmart"
    start_urls = ['http://help.walmart.com/app']
    def parse(self, response):
        ####### start from home page & follow category links 
        # 1358 1436 1486 
        for href in response.css('#category-list_1436 a::attr(href)'):
            yield response.follow(href,self.parse_cat)

    ###### function to parse category page and follow
    def parse_cat(self, response):
        for href in response.css('.rn_Content a::attr(href)'):
            yield response.follow(href, self.parse_question)
        for href in response.css('a#rn_Paginator_7_Forward::attr(href)'):
            yield response.follow(href, callback=self.parse_cat)

    def parse_question(self, response):
        question = response.css('#rn_AnswerText h1::text').extract()[0]
        yield {
            'question': question,
            'answer': response.css('#rn_AnswerText').xpath('.//p/text()|.//h3/text()|.//ol/li/text()|.//ul/li/text()').extract(),
            
        }