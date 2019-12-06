# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ZhihuAnswersSpiderItem(scrapy.Item):
    # 问题ID
    question_id = scrapy.Field()
    # 问题标题
    question_title = scrapy.Field()
    # 问题创建时间
    question_created = scrapy.Field()
    # 问题链接
    question_url = scrapy.Field()
    # 用户名
    author_name = scrapy.Field()
    # 用户链接
    author_url = scrapy.Field()
    # 用户简介
    author_headline = scrapy.Field()
    # 回答链接
    answer_url = scrapy.Field()
    # 回答创建时间
    answer_created_time = scrapy.Field()
    # 回答更新时间
    answer_updated_time = scrapy.Field()
    # 回答点赞数
    answer_voteup_count = scrapy.Field()
    # 回答评论数
    answer_comment_count = scrapy.Field()
    # 回答内容
    answer_content = scrapy.Field()
    # 回答图片列表
    img_urls = scrapy.Field()

class AcfunFollowUpdateItem(scrapy.Item):
    # 投稿标题
    content_title = scrapy.Field()
    # 名字
    up_name = scrapy.Field()
    # 投稿日期
    content_date = scrapy.Field()
    # 稿件链接
    content_url = scrapy.Field()
    # 稿件弹幕
    content_danmu = scrapy.Field()
    # 稿件评论
    content_discuss = scrapy.Field()
    # 稿件观看
    content_view = scrapy.Field()
    # 稿件类型
    content_type = scrapy.Field()
    # 稿件ID
    content_id = scrapy.Field()
    # up主页
    up_url = scrapy.Field()
    # 关注数量
    up_flow = scrapy.Field()
    # 粉丝数量
    up_fans = scrapy.Field()
    # 投稿数量
    up_contribute = scrapy.Field()
    # 个人简介
    up_desc = scrapy.Field()