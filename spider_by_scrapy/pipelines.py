# -*- coding: utf-8 -*-

import os
import hashlib

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.utils.python import to_bytes
from scrapy.pipelines.images import ImagesPipeline
import pymysql

class BaseMysqlPipelines():
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host = crawler.settings.get('MYSQL_HOST'),
            port = crawler.settings.get('MYSQL_PORT'),
            database = crawler.settings.get('MYSQL_DATABASE'),
            user = crawler.settings.get('MYSQL_USER'),
            password = crawler.settings.get('MYSQL_PASSWORD'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(host=self.host, port=int(self.port), db=self.database, user=self.user, password=self.password)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()


class ZhihuAnswersSpiderImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        image_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        # 图片保存在用户名路径下
        return f'{request.meta["img_dir"]}/{image_guid}.jpg'

    def get_media_requests(self, item, info):
        # 传递用户名+问题作为文件夹名称
        return [Request(x, meta={'img_dir': item['author_name']+'_'+item['question_title']}) for x in item['img_urls']]

    def item_completed(self, results, item, info):
        path = [x['path'] for ok, x in results if ok]
        if not path:
            raise DropItem(f'{item["author_name"]} download failed')
        return item


class ZhihuAnswersSpiderMysqlPipelines(BaseMysqlPipelines):
    def process_item(self, item, spider):
        item['img_urls'] = ','.join(item['img_urls'])
        data = dict(item)
        table = 'zhihu_answers_spider'
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))

        sql = f'INSERT INTO {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'
        update = ','.join([" {key} = %s".format(key=key) for key in data])
        sql += update
        try:
            if self.cursor.execute(sql, tuple(data.values())*2):
                self.db.commit()
        except Exception as e:
            print(e.args)
            self.db.rollback()

        return item


class AcfunFollowUpdateMysqlPipelines(BaseMysqlPipelines):
    def process_item(self, item, spider):
        data = dict(item)
        table = 'acfun_follow_update'
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = f'INSERT INTO {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'
        update = ','.join([" {key} = %s".format(key=key) for key in data])
        sql += update
        try:
            if self.cursor.execute(sql, tuple(data.values())*2):
                self.db.commit()
        except Exception as e:
            print(e.args)
            self.db.rollback()
        return item


class NovelBiqukanLocalPipelines():
    def __init__(self):
        self.name = ''

    def process_item(self, item, spider):
        novel_dir = './result/novel_biqukan/' + item.get('collection') + '/'
        if not os.path.exists(novel_dir):
            os.makedirs(novel_dir)

        with open(novel_dir + item.get('title').replace(r'/', '').replace(r'\\', '').replace(':', '').replace('*',
                                                                                                              '').replace(
                '"', '').replace('<', '').replace('>', '').replace('|', '').replace('?', '').replace('%',
                                                                                                     '').strip() + '.txt',
                  'w', encoding='utf-8') as f:
            f.write(item.get('title') + '\n\n')
            f.write(item.get('content') + '\n\n')

        print(item.get('title'), '下载完成！')
        return item


class UnsplashSpiderImagePipelines(ImagesPipeline):
    def get_media_requests(self, item, info):
        return Request(item.get('urls'))

    def item_completed(self, results, item, info):
        print(results)
        path = [x['path'] for ok, x in results if ok]
        if not path:
            raise DropItem('unsplash images downloads failed')
        return item

class UnsplashSpiderMysqlPipelines(BaseMysqlPipelines):
    def process_item(self, item, spider):
        print(item)
        data = dict(item)
        table = 'unsplash_images'
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))

        sql = f'INSERT INTO {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'
        update = ','.join([" {key} = %s".format(key=key) for key in data])
        sql += update
        try:
            if self.cursor.execute(sql, tuple(data.values())*2):
                self.db.commit()
        except Exception as e:
            print(e.args)
            self.db.rollback()

        return item

