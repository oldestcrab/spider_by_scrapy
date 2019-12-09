#!/usr/bin/env python
# encoding: utf-8

# @version: 0.1
# @file: unsplash_spider.py
# @author: oldestcrab
# @license: MIT Licence
# @software: PyCharm
# @time: 2019/12/9 21:25
# @description： unsplash网站图片爬取

import json

import scrapy
from scrapy import Request
from spider_by_scrapy.items import UnsplashItem


class Unsplash(scrapy.Spider):
    name = 'unsplash_spider'
    start_urls = ['https://unsplash.com/napi/collections/3356570/photos?page=1&per_page=30&order_by=latest']
    allow_domains = ['www.unsplash.com']

    page_last = 11
    page_now = 2

    def parse(self, response):
        doc = json.loads(response.text)
        # print(len(doc))
        for i in doc:
            item = UnsplashItem()
            item['title'] = i.get('alt_description')
            item['update_time'] = i.get('updated_at').split('T')[0]
            try:
                item['urls'] = i.get('urls').get('full')
            except:
                pass
            try:
                item['username'] = i.get('user').get('username')
            except:
                pass
            try:
                item['user_url'] = i.get('user').get('links').get('html')
            except:
                pass

            yield item

        if self.page_now < self.page_last:
            next_url = 'https://unsplash.com/napi/collections/3356570/photos?page=' + str(
                self.page_now) + '&per_page=30&order_by=latest'
            self.page_now += 1

            yield Request(next_url, callback=self.parse)

