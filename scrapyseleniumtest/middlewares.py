# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from logging import getLogger

from scrapy import signals
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger


class SeleniumMiddleware():
    def __init__(self, timeout=None):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        # self.browser = webdriver.PhantomJS(service_args=service_args)
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        # self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        """
        用PhantomJS抓取页面
        :param request: Request对象
        :param spider: Spider对象
        :return: HtmlResponse
        """
        # 通过request的meta属性获取当前需要爬取的页码
        # self.logger.debug('PhantomJS is starting')
        self.logger.debug('Chrome is starting')
        page = request.meta.get('page', 1)
        try:
            # 调用PhantomJS对象的get()方法访问Request对应的URL，随后处理等待和翻页
            self.browser.get(request.url)
            if page > 1:
                # 页码＞1，跳页操作，否则等待加载页面
                # 翻页操作：先获取页码输入框，赋值为input，然后获取“确定”按钮，赋值为submit，先清空输入框，clear()再调用
                # send_keys()方法将页码填充到输入框，点击“确定”
                input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
                )
                submit = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')) )
                input.clear()
                input.send_keys(page)
                submit.click()
            # 确定跳转正确：判断当前高亮页码数是当前的页码数,css选择器和当前跳转的页码通过参数传给text_to_be...
            self.wait.until(EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page)))
            # 最终要等到商品信息加载出来，选择器对应页面内容是每个商品的信息快
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.m-itemlist .items .item')))
            # 用PhantomJS对象的page_source属性获得当前页面的源代码，用它直接构造并返回一个HtmlResponse对象，需要传入多个参数
            # 如url,body等，是它的基础属性
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request,encoding='utf-8',status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)


    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),)

                   # service_args=crawler.settings.get('PHANTOMJS_SERVICE_ARGS'))


# class ScrapyseleniumtestSpiderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the spider middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_spider_input(self, response, spider):
#         # Called for each response that goes through the spider
#         # middleware and into the spider.
#
#         # Should return None or raise an exception.
#         return None
#
#     def process_spider_output(self, response, result, spider):
#         # Called with the results returned from the Spider, after
#         # it has processed the response.
#
#         # Must return an iterable of Request, dict or Item objects.
#         for i in result:
#             yield i
#
#     def process_spider_exception(self, response, exception, spider):
#         # Called when a spider or process_spider_input() method
#         # (from other spider middleware) raises an exception.
#
#         # Should return either None or an iterable of Response, dict
#         # or Item objects.
#         pass
#
#     def process_start_requests(self, start_requests, spider):
#         # Called with the start requests of the spider, and works
#         # similarly to the process_spider_output() method, except
#         # that it doesn’t have a response associated.
#
#         # Must return only requests (not items).
#         for r in start_requests:
#             yield r
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
#
#
# class ScrapyseleniumtestDownloaderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the downloader middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_request(self, request, spider):
#         # Called for each request that goes through the downloader
#         # middleware.
#
#         # Must either:
#         # - return None: continue processing this request
#         # - or return a Response object
#         # - or return a Request object
#         # - or raise IgnoreRequest: process_exception() methods of
#         #   installed downloader middleware will be called
#         return None
#
#     def process_response(self, request, response, spider):
#         # Called with the response returned from the downloader.
#
#         # Must either;
#         # - return a Response object
#         # - return a Request object
#         # - or raise IgnoreRequest
#         return response
#
#     def process_exception(self, request, exception, spider):
#         # Called when a download handler or a process_request()
#         # (from other downloader middleware) raises an exception.
#
#         # Must either:
#         # - return None: continue processing this exception
#         # - return a Response object: stops process_exception() chain
#         # - return a Request object: stops process_exception() chain
#         pass
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
