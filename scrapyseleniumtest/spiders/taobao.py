# -*- coding: utf-8 -*-
from urllib.parse import quote

import scrapy
from scrapy import Request

from ..items import ProductItem


class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    allowed_domains = ['www.taobao.com']
    base_url = 'http://www.taobao.com/search?q='

    def start_requests(self):
        # 遍历分页页码，构造生成Request,分页页码用meta参数传递，设置dont_filter不去重
        # quote()方法将内容转化为URL编码的格式，中文字符
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = self.base_url + quote(keyword)
                yield Request(url=url, callback=self.parse, meta={'page': page}, dont_filter=True)

    def parse(self, response):
        # xpath规则：//从匹配选择的当前节点选择文档中的节点，不考虑位置 最前面加.选取当前节点内部元素 [1]是谓语，选取第一个xxx
        # /text()节点的内部文本，具体内容extract() strip()删除开头结尾空字符 ''.join()序列中的元素以字符连接为新字符串
        products = response.xpath(
            '//div[@id="mainsrp-itemlist"]//div[@class="items"][1]//div[contains(@class, "item")]'
        )
        for product in products:
            item = ProductItem()
            item['price'] = ''.join(product.xpath('.//div[contains(@class, "price")]//text()').extract()).strip()
            item['title'] = ''.join(product.xpath('.//div[contains(@class, "title")]//text()').extract()).strip()
            item['shop'] = ''.join(product.xpath('.//div[contains(@class, "shop")]//text()').extract()).strip()
            item['image'] = ''.join(product.xpath('.//div[@class="pic"]//img[contains(@class, "img")]/@data-src').extract()).strip()
            item['deal'] = product.xpath('.//div[contains(@class, "deal-cnt")]//text()').extract_first()
            item['location'] = product.xpath('.//div[contains(@class, "location")]//text()').extract_first()
            yield item

