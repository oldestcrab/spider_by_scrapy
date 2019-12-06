#!/usr/bin/env python
# encoding: utf-8

# @version: 0.1
# @file: acfun_follow_update.py
# @author: oldestcrab
# @license: MIT Licence
# @software: PyCharm
# @time: 2019/12/6 14:28
# @description： 爬取A站某用户的关注UP主一周内的更新信息

import scrapy
from scrapy import Request
import json
from lxml import etree
from spider_by_scrapy.items import AcfunFollowUpdateItem
import time
import re

class AcfunFollowUpdateSpider(scrapy.Spider):
    name = 'acfun_follow_update'
    allow_domain = ['www.acfun.cn']
    start_urls = ['https://www.acfun.cn/space/next?uid=973167&type=flow&orderBy=2&pageNo=1']

    def parse(self, response):
        now = time.strftime('%Y/%m/%d', time.localtime())
        # json字符串转换为dict
        doc = json.loads(response.text)

        html_str = doc['data'].get('html', '')
        # 格式化html
        html = etree.HTML(html_str)
        up_list = html.xpath('//figure')
        # 获取关注的up的信息
        for up in up_list:
            up_url = 'https://www.acfun.cn' + up.xpath('.//a[@class="name"]/@href')[0]
            up_name = up.xpath('string(.//a[@class="name"])')
            up_flow = up.xpath('string(.//span[@class="flow"]/span)')
            up_fans = up.xpath('string(.//span[@class="fans"]/span)')
            up_contribute = up.xpath('string(.//span[@class="contribute"]/span)')
            up_desc = up.xpath('string(.//p[@class="desc"])')

            up_info = {
                'up_url':up_url,
                'up_name':up_name,
                'up_flow':up_flow,
                'up_fans':up_fans,
                'up_contribute':up_contribute,
                'up_desc':up_desc,
            }
            # 查看用户本周更新
            yield Request(up_url, callback=self.check_update, meta={'up_info':up_info})

        # 获取下一页
        totalPage = doc['data']['page'].get('totalPage', 0)
        # 获取当前页
        page_now = doc['data']['page'].get('pageNo', 0)
        # 当前页小于下一页时，获取下一页的数据
        if page_now <= totalPage:
            url_next = 'https://www.acfun.cn/space/next?uid=973167&type=flow&orderBy=2&pageNo=' + str(page_now+1)
            # 继续获取下一页
            yield  Request(url_next, callback=self.parse)


    def check_update(self, response):
        # 获取一个星期前的当前时刻
        limit = time.localtime(time.time() - 259200)
        if limit.tm_mon < 10:
            mon = '0' + str(limit.tm_mon)
        else:
            mon = str(limit.tm_mon)
        if limit.tm_mday < 10:
            day = '0' + str(limit.tm_mday)
        else:
            day = str(limit.tm_mday)
        last_week = str(limit.tm_year) + '/' + mon + '/' + day
        # print('时间段\t'+last_week+'  ————  NOW')
        up_info = response.meta['up_info']
        video_list = response.xpath('//div[@id="listVideo"]/div/a')
        for video in video_list:
            item = AcfunFollowUpdateItem()
            item['content_title'] = video.xpath('./figure/@data-title').extract_first()
            item['up_name'] = up_info['up_name']
            item['content_date'] = video.xpath('string(.//p[@class="date"])').extract_first()
            item['content_url'] = 'https://www.acfun.cn' + video.xpath('./figure/@data-url').extract_first()
            item['content_danmu'] = video.xpath('string(.//span[@class="danmu"]/span)').extract_first()
            item['content_view'] = video.xpath('string(.//span[@class="view"]/span)').extract_first()
            item['content_type'] = 'video'
            item['content_id'] = video.xpath('./figure/@data-vid').extract_first()
            item['up_url'] = up_info['up_url']
            item['up_flow'] = up_info['up_flow']
            item['up_fans'] = up_info['up_fans']
            item['up_contribute'] = up_info['up_contribute']
            item['up_desc'] = up_info['up_desc']
            if item['content_date'] > last_week:
                print('*'*50)
                print('标题\t\t', item['content_title'])
                print('up\t\t', up_info['up_name'])
                print('url\t\t', item['content_url'])
                print('弹幕\t\t', item['content_danmu'])
                print('更新时间\t', item['content_date'])
                print('*'*50 + '\n')

                yield item

        article_list = response.xpath('//div[@id="listArticle"]/div/figure')
        for article in article_list:
            item = AcfunFollowUpdateItem()
            item['content_title'] = article.xpath('./a/@title').extract_first()
            item['up_name'] = up_info['up_name']
            things =article.xpath('string(.//p[@class="crumbs"])').extract_first()
            item['content_date'] = re.search(r'发布于\s(.*?)\s\/', things).group(1)
            item['content_url'] = 'https://www.acfun.cn' + article.xpath('./a/@href').extract_first()
            item['content_discuss'] = re.search(r'\s\/\s(.*?)条评论', things).group(1)
            item['content_view'] = re.search(r'条评论\s\/\s(.*?)人围观', things).group(1)
            item['content_type'] = 'article'
            item['content_id'] = re.search(r'atomid":"(.*?)",',article.xpath('./@data-wbinfo').extract_first()).group(1)
            item['up_url'] = up_info['up_url']
            item['up_flow'] = up_info['up_flow']
            item['up_fans'] = up_info['up_fans']
            item['up_contribute'] = up_info['up_contribute']
            item['up_desc'] = up_info['up_desc']
            if item['content_date'] > last_week:

                yield item

