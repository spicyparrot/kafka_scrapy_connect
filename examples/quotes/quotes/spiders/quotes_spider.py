import os
import sys
import json
import logging

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, os.path.abspath(f'{SCRIPT_DIRECTORY}/../../../../'))

from kafka_scrapy_connect.spiders import KafkaListeningSpider

class TestKafkaSpider(KafkaListeningSpider):
    name = "quotes"

    # Override process_kafka_message to suit your serializer type or use default method which can parse JSON / string serialized messages
    # Method needs to return a URL to crawl / scrape
    # def process_kafka_message(self, message):
    #     logging.info('Custom process kafka message - received message')
    #     json_obj = json.loads(message.value())
    #     url = json_obj['url']
    #     return url


    def parse(self, response):
        logging.info(f'Received a response ...{response}')
        for quote in response.xpath('//div[@class="quote"]'):
            yield {
                'text' : quote.xpath('./span[@class="text"]/text()').extract_first(),
                'author' : quote.xpath('.//small[@class="author"]/text()').extract_first(),
                'tags' : quote.xpath('.//div[@class="tags"]/a[@class="tag"]/text()').extract()
            }