import os
import sys
import logging
from scrapy.utils.log import configure_logging

BOT_NAME = "quotes"

SPIDER_MODULES = ["quotes.spiders"]
NEWSPIDER_MODULE = "quotes.spiders"

ITEM_PIPELINES = {
    'kafka_scrapy_connect.pipelines.KafkaPublishPipeline': 100
    }

# Scrapy kafka connect settings
SCRAPY_KAFKA_HOSTS  = 'localhost:29092'
SCRAPY_INPUT_TOPIC  = 'ScrapyInput'
SCRAPY_OUTPUT_TOPIC = 'ScrapyOutput'
SCRAPY_ERROR_TOPIC = 'ScrapyErrors'
SCRAPY_STATS_TOPIC = 'ScrapyStats'

SCRAPY_KAFKA_PRODUCER_KEY = ''
SCRAPY_KAFKA_PRODUCER_CALLBACKS = False
SCRAPY_PRODUCER_CONFIG = {
    'queue.buffering.max.ms' : 1,
    'linger.ms' : 5
}

SCRAPY_CONSUMER_CONFIG = {
    'group.id':'example-crawler',
    'fetch.wait.max.ms': 10,
    'max.poll.interval.ms': 600000,
    'auto.offset.reset': 'earliest'
}

# LOGSTATS_INTERVAL = 60.0
# LOGSTATS_SUMMARY_INTERVAL = "DAILY"

EXTENSIONS = {
   'scrapy.extensions.logstats.LogStats': None,
   'kafka_scrapy_connect.extensions.KafkaLogStats': 500
}

LOG_LEVEL = 'INFO'  # to only display errors
LOG_FORMAT = '%(asctime)s - %(levelname)8s - %(message)s'