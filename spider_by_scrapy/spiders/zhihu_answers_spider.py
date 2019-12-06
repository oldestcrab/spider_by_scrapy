#!/usr/bin/env python
# encoding: utf-8

# @version: 0.1
# @file: zhihu_answers_spider.py
# @author: oldestcrab
# @license: MIT Licence
# @software: PyCharm
# @time: 2019/12/6 14:28
# @description： 爬取知乎某个问题下点赞超过1000的回答信息

import json
import time
import re

import scrapy

from spider_by_scrapy.items import ZhihuAnswersSpiderItem


class ZhihuAnswersSpider(scrapy.Spider):
    name = 'zhihu_answers_spider'
    allow_domains = ['www.zhihu.com']
    start_urls = [
        'https://www.zhihu.com/api/v4/questions/35931586/answers?include=data[*].comment_count,,content,voteup_count,created_time,updated_time,question&limit=20&platform=desktop&sort_by=default'
    ]
    offset = 1

    def parse(self, response):
        # 转化为字典
        data = json.loads(response.text)
        # 获取数据
        result = data.get('data')
        if isinstance(result, list):
            for i in result:
                item = ZhihuAnswersSpiderItem()
                # 问题ID
                item['question_id'] = i.get('question').get('id') if i.get('question') else None
                # 问题标题
                item['question_title'] = i.get('question').get('title') if i.get('question') else None
                # 问题创建时间
                item['question_created'] = i.get('question').get('created') if i.get('question') else None
                # 转换为日期格式
                if item['question_created']:
                    item['question_created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(item['question_created'])))
                # 问题链接
                item['question_url'] = i.get('question').get('url') if i.get('question') else None
                item['question_url'] = item['question_url'].replace('/api/v4/questions', '/question')
                # 用户名
                item['author_name'] = i.get('author').get('name') if i.get('author') else None
                # 用户链接
                item['author_url'] = i.get('author').get('url') if i.get('author') else None
                item['author_url'] = item['author_url'].replace('api/v4/', '')
                # 用户简介
                item['author_headline'] = i.get('author').get('headline') if i.get('author') else None
                # 回答链接
                item['answer_url'] = i.get('url')
                item['answer_url'] = item['answer_url'].replace('https://www.zhihu.com/api/v4/answers', item['question_url']+'/answer')
                # 回答创建时间
                item['answer_created_time'] = i.get('created_time')
                if item['answer_created_time']:
                    item['answer_created_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(item['answer_created_time'])))
                # 回答更新时间
                item['answer_updated_time'] = i.get('updated_time')
                if item['answer_updated_time']:
                    item['answer_updated_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(item['answer_updated_time'])))
                # 回答点赞数
                item['answer_voteup_count'] = i.get('voteup_count')
                # 回答评论数
                item['answer_comment_count'] = i.get('comment_count')
                # 回答内容
                item['answer_content'] = i.get('content')
                # 获取回答中的所有图片
                img_pattern = re.compile(r'\sdata-original=\"(.*?\/.*?\.[jpbg][pmin]\w+)\"{1}', re.I)
                item['img_urls'] = img_pattern.findall(item['answer_content'])
                item['img_urls'] = list(set(item['img_urls']))
                # print(item)
                # 只爬取大于1000点赞数的
                if item['answer_voteup_count']:
                    if int(item['answer_voteup_count']) > 1000:
                       yield item

        if self.offset < 1000:
            next_url = self.start_urls[0] + f'&offset={self.offset*5}'
            # print(next_url)
            self.offset += 1
            # 获取下一组数据
            yield scrapy.Request(next_url, callback=self.parse)