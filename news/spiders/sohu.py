import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service  # 导入Edge浏览器的Service类
import requests
import scrapy
from ..items import NewsItem
from datetime import datetime
from fake_useragent import UserAgent
import re
class EntSpider(scrapy.Spider):
    # 创建Edge选项
    edge_options = Options()
    edge_options.add_argument("--headless")  # 无界面模式
    driver_path = "news/spiders/msedgedriver.exe"
    # 创建Edge WebDriver对象
    service =Service(driver_path)
    driver = webdriver.Edge(service=service,options=edge_options)
    api_url = "https://odin.sohu.com/odin/api/blockdata"
    categories = ["明星", "综艺", "影视音乐", "网络红人"]
    api_dict={}
    for category in categories:
        with open("news/spiders/"+category+"api.txt")  as f:
            temp_dict = json.load(f)
            api_dict[category]=temp_dict
    # logging.info(api_dict)
    name = 'sohu'
    allowed_domains = ['yule.sohu.com','www.sohu.com','odin.sohu.com']
    start_urls = ['http://yule.sohu.com']
    ua = UserAgent()

    def extract_date_time(self,text):
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    def get_reading_count(self,url):
        try:
            edge_options = Options()
            edge_options.add_argument("--headless")  # 无界面模式
            edge_options.add_argument("user-agent="+str(self.ua.random))
            self.driver.options =edge_options
            self.driver.get(url)
            reading_num = self.driver.find_element(By.XPATH, '//div[@class="read-wrap"]/span[@class="read-num"]/em').text
            time.sleep(1)
            return reading_num
        except:
            return None
    def convert_to_datetime(self,date_string):
        try:
            date_format = "%Y-%m-%d %H:%M"
            datetime_obj = datetime.strptime(date_string, date_format)
            return datetime_obj
        except :
            self.logger.info("Error wile coverting datetime")
            return None
    def parse(self,response,**kwargs):
       a_labels = response.xpath('//div[@class="nav_header"]/div[@class="nav_container"]/a[@class="nav_item"]')
       for a_label in a_labels:
           category = a_label.xpath('./text()').extract_first()
           url ="http://www.sohu.com"+a_label.xpath('./@href').extract_first()
           category= category.strip()
           if category in self.categories:
               yield scrapy.Request(url=url,callback=self.parse_kind_page,meta ={"category":category})
    def get_reading_num(self,reading_count):
        pattern = r'(\d+\.\d+|\d+)'
        match = re.search(pattern, reading_count)
        if match:
            temp  = float(match.group())
            if '万' in reading_count:
                temp =temp*10000
            return int(temp)
        else:
            return None


    def parse_kind_page(self,response):
        category = response.meta['category']
        headers = {'User-Agent': self.ua.random}
        data = self.api_dict[category]['data']
        for page in range(1,20):
            data["resourceList"][0]["content"]["page"]=page
            page_json = requests.post(url=self.api_url,headers=headers,json=data).json()
            if page_json['code']!=0:
                break
            datalist = page_json["data"]["TPLFeedMul_2_9_feedData"]["list"]
            try:
                for item_data in datalist:
                    cover =item_data['cover']
                    brief = item_data['brief']
                    title =item_data["title"]
                    extractInfo =item_data["extraInfo"]
                    detail_url ="https://www.sohu.com"+item_data["url"]
                    yield scrapy.Request(url =detail_url,callback=self.parse_detail,meta={"category":category,"url":detail_url,"title":title,"brief":brief,"extractInfo":extractInfo,"cover":cover})
            except:
                break
            time.sleep(1)


    def parse_detail(self,response):
        item =NewsItem()
        article_content =""
        text_list = response.xpath('//article[@id="mp-editor"]//text()').extract()
        # self.logger.info()
        for text in text_list:
            article_content=article_content+text
        temp_texts =response.xpath('//div[@class="article-info"]/span[@id="news-time"]//text()').extract()
        temp_text = ''.join(temp_texts)
        publication_time = self.extract_date_time(temp_text)
        # self.logger.info("pulication_time:"+publication_time)
        # reading_count = response.xpath('//div[@class="read-wrap"]/span[@class="read-num"]/em/text()').extract_first().strip()
        item['url'] =response.meta['url']
        item["category"] = response.meta['category']
        item["title"]=response.meta['title']
        item['brief'] =response.meta["brief"]
        item["cover"]= response.meta["cover"]
        mixed_info=response.meta["extractInfo"].split('·')
        item["publication_press"]=mixed_info[0].strip()
        item["publication_time"] =self.convert_to_datetime(publication_time)
        if len(mixed_info)>=3:
            item["reading_count"] =mixed_info[2].strip()
        else:
            item["reading_count"] =self.get_reading_count(item['url'])
            # item['reading_count'] =None
        if len(article_content)>10000:
            article_content=article_content[:9999]
        item['article_content']=article_content
        item['reading_num']  = self.get_reading_num(item['reading_count'])
        yield item










