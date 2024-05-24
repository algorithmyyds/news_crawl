# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# pipelines.py
import logging
import pymysql
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

class MySQLPipeline:
    def __init__(self):
        settings = get_project_settings()
        self.host = settings.get('MYSQL_HOST')
        self.port = settings.get('MYSQL_PORT')
        self.database = settings.get('MYSQL_DATABASE')
        self.user = settings.get('MYSQL_USER')
        self.password = settings.get('MYSQL_PASSWORD')
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            db=self.database,
            user=self.user,
            password=self.password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        try:
            table = 'basic_info'  # 表名
            columns = ', '.join(item.keys())
            placeholders = ', '.join(['%s'] * len(item))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, list(item.values()))
            self.conn.commit()
            self.logger.debug("插入成功")
            return item
        except Exception as e:
            self.conn.rollback()
            self.logger.debug(f"Failed to save item to MySQL: {e}")

