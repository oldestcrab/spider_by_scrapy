#!/usr/bin/env python
# encoding: utf-8

# @version: 0.1
# @file: novel_biqukan.py
# @author: oldestcrab
# @license: MIT Licence
# @software: PyCharm
# @time: 2019/12/6 15:59
# @description：爬取笔趣阁的某部小说

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from urllib.parse import quote
import re
from spider_by_scrapy.items import NovelBiqukanItem


class NovelBiqukanSpider(CrawlSpider):
    name = 'novel_biqukan'
    # start_urls = ['https://www.biqukan.com/50_50758/']
    allow_domains = ['www.biqukan.com']

    link_chapter = LinkExtractor(restrict_xpaths=('//dd/a'))

    rules = (
        Rule(link_chapter, callback='parse_chapter'),
    )

    novel_name = ''

    def parse_start_url(self, response):
        # item = NovelBiqukanItem()
        # item['collection'] = response.meta['novel_name']
        # return item
        self.novel_name = response.meta['novel_name']
        return []

    def start_requests(self):
        # 重写方法
        novel_name = input('请输入小说名字(退出请输入 exit):\t')
        while not novel_name:
            novel_name = input('\n请输入小说名字(退出请输入 exit):\t')
        if novel_name == 'exit':
            return
            # 搜索书籍
        start_url = 'https://so.biqusoso.com/s.php?ie=utf-8&siteid=biqukan.com&q=' + quote(novel_name)
        # print(start_url)
        # 解析搜索页面
        yield Request(start_url, callback=self.select_book)

    def select_book(self, response):
        # 解析搜索页面
        # 获取书籍列表
        novel_list = response.xpath('//div[@class="search-list"]/ul/li')
        del novel_list[0]
        novel_dict = {}
        for novel in novel_list:
            key = novel.xpath('string(./span[@class="s1"])').extract_first()
            value = [novel.xpath('string(./span[@class="s2"])').extract_first(),
                     novel.xpath('string(./span[@class="s4"])').extract_first(),
                     novel.xpath('./span[@class="s2"]/a/@href').extract_first()]
            novel_dict[key] = value
        # 显示所有书籍
        for key, value in novel_dict.items():
            print(key, value[0] + '(' + value[1] + ')')
        novel_id = input('\n请输入要下载的书籍编号(退出请输入 exit)：\t')

        while not novel_id:
            novel_id = input('\n请输入要下载的书籍编号(退出请输入 exit)：\t')

        if novel_id == 'exit':
            return

            # 返回初始url
        if novel_id in novel_dict.keys():

            start_url = novel_dict[novel_id][2]
            novel_name = novel_dict[novel_id][0]
            # print(start_url)
            # 返回初始response
            yield Request(start_url, dont_filter=True, meta={'novel_name': novel_name})
        else:
            print('\n请输入正确的书籍编号！')

    def parse_chapter(self, response):

        item = NovelBiqukanItem()
        item['collection'] = self.novel_name

        title = response.xpath('string(//h1)').extract_first().strip('\r\n').replace(u'\u3000', u' ').replace(u'\xa0',
                                                                                                              u' ')
        item['title'] = title

        title_id = title.split(' ')[0].replace('第', '').replace('章', '')
        if title_id.isdigit():
            item['title_id'] = title_id
        else:
            try:
                # 转换为中文数字
                item['title_id'] = self.chinese_to_digit(title_id)
            except:
                pass

        # print(item['title_id'])
        content = response.xpath('string(//div[@class="showtxt"])').extract_first()
        item['content'] = re.sub(r'\(https:.*biqukan\.com', '', content).strip('\r').replace(u'\u3000', u'\n').replace(
            u'\xa0', u' ')

        yield item

    def chinese_to_digit(self, chinese):
        """
        把所有中文数字转换为阿拉伯数字(仅支持不超过10万的数字转换)
        :params chinese:中文数字
        """
        dict_chinese_to_digit = {
            '零': '0',
            '一': '1',
            '二': '2',
            '两': '2',
            '三': '3',
            '四': '4',
            '五': '5',
            '六': '6',
            '七': '7',
            '八': '8',
            '九': '9',
            '十': '10',
            '百': '100',
            '千': '1000',
            '万': '10000',
        }

        num = []
        # 把所有中文数字转换为阿拉伯数字,放入一个列表
        for i in chinese:
            if i in dict_chinese_to_digit.keys():
                digit = dict_chinese_to_digit[i]
                num.append(digit)

        # 存储结果
        total = 0
        # 列表后一位>=10，与前一位相乘，再加起来。此步得到除个位之外的总和
        for i in range(len(num) - 1):
            if int(num[i + 1]) >= 10:
                total += int(num[i]) * int(num[i + 1])

        # 最后加上个位数
        if int(num[len(num) - 1]) < 10:
            total += int(num[len(num) - 1])

        # 十* 另外计算
        if chinese.startswith('十'):
            total = 0
            for i in range(len(num)):
                total += int(num[i])

        return total
