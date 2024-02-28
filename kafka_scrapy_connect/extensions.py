import logging
import sys
import os
import time
import datetime
import json
from twisted.internet import task, reactor
from scrapy import signals
from scrapy.exceptions import NotConfigured
from confluent_kafka import Producer as KafkaProducer

logger = logging.getLogger(__name__)

class KafkaLogStats:
    """
    Log basic scraping stats periodically and publish summaries to a Kafka topic for analysis
    """

    def __init__(self, stats, producer, topic, interval=60.0, summary_interval=300.0):
        """
        Initialize KafkaLogStats instance.

        Args:
            stats (object): Scrapy stats object.
            producer (object): Kafka producer object.
            topic (str): Kafka topic name.
            interval (float): Interval for logging stats (in seconds).
            summary_interval (float): Interval for publishing summary stats to Kafka (in seconds).
        """
        self.stats = stats
        self.interval = interval
        self.summary_interval = self.interval_to_seconds(summary_interval)
        self.multiplier = 60.0 / self.interval
        self.summary_task = None
        self.task = None
        self.producer = producer
        self.topic = topic

    @classmethod
    def from_crawler(cls, crawler):
        """
        Initialize KafkaLogStats instance from a Scrapy crawler.

        Args:
            crawler (object): Scrapy crawler instance.

        Returns:
            KafkaLogStats: Initialized KafkaLogStats instance.
        """
        kafka_hosts = crawler.settings.get('SCRAPY_KAFKA_HOSTS', 'localhost:9092')
        producer_config = crawler.settings.get('SCRAPY_PRODUCER_CONFIG', {})
        kafka_config = {'bootstrap.servers': kafka_hosts, **producer_config}
        topic = crawler.settings.get('SCRAPY_STATS_TOPIC', 'scrapy_kafka_item')
        kafka_producer = KafkaProducer(kafka_config)
        interval = crawler.settings.getfloat("KAFKA_LOGSTATS_INTERVAL",60.0)
        summary_interval = crawler.settings.get("KAFKA_LOGSTATS_SUMMARY_INTERVAL","DAILY")
        if not interval or not summary_interval:
            raise NotConfigured
        o = cls(crawler.stats, kafka_producer, topic, interval, summary_interval)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def interval_to_seconds(self,interval):
        if interval == 'DAILY':
            return 86400
        else:
            logger.info("Default kafka publish interval to 86400s (1day)")
            return 86400

    def spider_opened(self, spider):
        """
        Handle spider opened signal.
        """
        self.pagesprev = 0
        self.itemsprev = 0
        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)
        self.summary_log(spider)

    def log(self, spider):
        """
        Log basic scraping stats.
        """
        items = self.stats.get_value("item_scraped_count", 0)
        pages = self.stats.get_value("response_received_count", 0)
        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        self.pagesprev, self.itemsprev = pages, items
        msg = (
            "Crawled %(pages)d pages (at %(pagerate)d pages/min), "
            "scraped %(items)d items (at %(itemrate)d items/min) "
        )
        log_args = {
            "pages": pages,
            "pagerate": prate,
            "items": items,
            "itemrate": irate
        }
        logger.info(msg, log_args, extra={"spider": spider})

    def summary_log(self, spider,spider_closing=False):
        """
        Publish summary stats to Kafka.
        """
        items = self.stats.get_value("item_scraped_count", 0)
        pages = self.stats.get_value("response_received_count", 0)
        requests = self.stats.get_value("downloader/request_count", 0)
        responses = self.stats.get_value("downloader/response_count", 0)
        if items == 0 and pages == 0:
            logger.info("No stats available to publish.")
        else:
            start_time = self.stats.get_value("start_time")
            self.pagesprev, self.itemsprev = pages, items
            status_counts = self.get_response_status_counts()
            status_counts_str = ", ".join([f"{key}: {value}" for key, value in status_counts.items()])
            # Calculate the percentage of scraped items for the total number of crawled
            if requests != 0:
                scraped_percentage = (responses / requests) * 100
            else:
                scraped_percentage = 0
            elapsed_time = round(time.time() - start_time.timestamp(), 3)
            summary_log_args = {
                "pages_crawled": pages,
                "items_scraped": items,
                "avg pages/min":  self.round_value((pages / elapsed_time) * 60),
                "avg pages/hour": self.round_value((pages / elapsed_time) * 3600),
                "avg pages/day":  self.round_value((pages / elapsed_time) * 86400),
                "avg items/min":  self.round_value((items / elapsed_time) * 60),
                "avg items/hour": self.round_value((items / elapsed_time) * 3600),
                "avg items/day":  self.round_value((items / elapsed_time) * 86400),
                "successful_request_percentage": scraped_percentage,
                "http_status_counts": status_counts_str,
                "max_memory": self.stats.get_value("memusage/max", 0),
                "elapsed_time": self.round_value(time.time() - start_time.timestamp())
            }
            if spider_closing is False:
                logger.info(f'Publishing summary scrapy statistics to Kafka topic: {self.topic} every {self.summary_interval}s')
                self.producer.produce(self.topic, key=self.generate_kafka_key(), value=json.dumps(summary_log_args), callback=self.delivery_callback)
                # Reset stats
                self.reset_stats()
            else:
                logger.info(f'Spider is closing.... publishing final batch of closing statistics to Kafka topic: {self.topic}')
                self.producer.produce(self.topic, key=self.generate_kafka_key(True), value=json.dumps(summary_log_args), callback=self.delivery_callback)
            self.producer.poll(0)
            self.producer.flush()

        if spider_closing is False:
            # Schedule the summary log to be called at next interval
            next_summary_time = self.get_next_summary_time()
            seconds_until_next_summary = (next_summary_time - datetime.datetime.now()).total_seconds()
            logger.info(f'Next batch of stats will be sent at EOD at {next_summary_time.strftime("%Y-%m-%d %H:%M")} in {seconds_until_next_summary:.0f}s')
            task.deferLater(reactor, seconds_until_next_summary, self.summary_log, spider)

    def round_value(self, val):
        """
        Round value to 2 decimal places
        """
        return round(val,2)

    def delivery_callback(self, err, msg):
        """
        Kafka message delivery callback.
        """
        if err is not None:
            logger.error(f'Failed to publish message to stats topic: {msg.topic()}')
        else:
            logger.info(f'Produced stats message to {msg.topic()} [{msg.partition()}] @ {msg.offset()}')

    def get_next_summary_time(self):
        """
        Calculate the next time the summary log should run based on the configured interval.
        """
        current_time = datetime.datetime.now()
        interval = self.summary_interval / 60  # Convert summary_interval to minutes
        if interval == 1440:  # Daily
            # Calculate midnight of the next day
            next_day = current_time + datetime.timedelta(days=1)
            next_summary_time = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to hourly if interval is not recognized
            next_day = current_time + datetime.timedelta(days=1)
            next_summary_time = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
        return next_summary_time

    def generate_kafka_key(self,process_closing=False):
        """
        Generates a key for the kafka message
        """
        if process_closing is False:
            previous_day = datetime.date.today() - datetime.timedelta(days=1)
            return previous_day.strftime('%Y-%m-%d')
        else:
            return datetime.datetime.now().strftime('%Y-%m-%d')

    def get_response_status_counts(self):
        """
        Get HTTP response status counts.
        """
        status_codes = [
            '200', '201', '202', '203', '204', '205', '206', '207', '208', '226',
            '300', '301', '302', '303', '304', '305', '306', '307', '308',
            '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413', '414', '415', '416', '417', '418', '421', '422', '423', '424', '425', '426', '429', '431', '451'
            ]
        status_counts = {}
        for code in status_codes:
            count = self.stats.get_stats().get(f"downloader/response_status_count/{code}",0)
            if count > 0:
                status_counts[code] = count
        return status_counts

    def reset_stats(self):
        """
        Reset stats at midnight.
        """
        # Reset the stats dictionary
        logger.warn('Resetting stats dictionary at EOD')
        self.stats.clear_stats()
        # Reset the previous page and item counts
        self.itemsprev = 0
        self.pagesprev = 0

    def spider_closed(self, spider, reason):
        """
        Handle spider closed signal and publish stats to kafka
        """
        self.summary_log(spider,True)
        if self.task and self.task.running:
            self.task.stop()
        if self.summary_task and self.summary_task.running:
            self.summary_task.stop()