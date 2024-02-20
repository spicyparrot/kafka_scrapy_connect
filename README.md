[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-3918) [![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-31013/) [![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3117/)
## Kafka Scrapy Connect

`kafka_scrapy_connect` is a custom Scrapy library that aims to integrates Scrapy with Kafka.

It consists of two main components: spiders and pipelines, which interact with Kafka for message consumption and item publishing.

This project has been motivated by the great work undertaken in: https://github.com/dfdeshom/scrapy-kafka. `kafka_scrapy_connect` utilises [Confluent's](https://github.com/confluentinc/confluent-kafka-python) Kafka Python client, under the hood, to provide high-level producer and consumer features.
## Features

- **Integration with Kafka** 📈
  - Enables communication between Scrapy spiders and Kafka topics for efficient data processing.
  - Through partitions and consumer groups message processing can be parallelised across multiple spiders!
  - Reduces overhead and improves throughput by giving the user the ability to consume messages in batches  📈

  
- **Customisable Settings** 🛠️
  - Provides flexibility through customisable configuration for both consumers and producers.

- **Error Handling** 🚑
  - Automatically handles network errors during crawling and publishes failed URLs to a designated output topic. 

- **Serialisation Customisation**: 
  - Allows users to customize how Kafka messages are deserializsd by overriding the process_kafka_message method.

## Installation

You can install `kafka_scrapy_connect` via pip:
```
pip install kafka_scrapy_connect
```

## Example

To bring up a spider using `kafka_scrapy_connect` and kafka, execute the steps below:

1. Create a virtual environment and install requirements
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a local kafka cluster with required topics:

```bash
./examples/kafka/kafka_start.sh --input-topic ScrapyInput,1 --output-topic ScrapyOutput,1 --error-topic ScrapyError,1
```

3. Initiate spider:
```bash
cd examples/quotes && scrapy crawl quotes
```

4. Publish a message to the input kafka topic and watch the spider consume and process the mesasge 🪄

5. When you're finished, exit the spider and clean up your local kafka cluster running:
```bash
./examples/kafka/kafka_stop.sh
```

## Usage

### Custom Settings
`kafka_scrapy_connect` supports the following custom settings:

- `SCRAPY_KAFKA_HOSTS`  - A list of kafka broker hosts. (Default: `localhost:29092`)
- `SCRAPY_INPUT_TOPIC`  - Topic from which the spider[s] *consumes* messages from. (Default: `ScrapyInput`)
- `SCRAPY_OUTPUT_TOPIC` - Topic where scraped items are published. (Default: `ScrapyOutput`)
- `SCRAPY_ERROR_TOPIC`  - Topic for publishing URLs that failed due to *network errors*. (Default: `ScrapyError`)
- `SCRAPY_CONSUMER_CONFIG` - Additional configuration options for Kafka consumers (see [here](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md))
- `SCRAPY_PRODUCER_CONFIG` - Additional configuration options for Kafka producers (see [here](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md))
- `SCRAPY_KAFKA_PRODUCER` - Key used for partitioning messages in Kafka producer (Default: `""` *Roundrobin*)
- `SCRAPY_KAFKA_PRODUCER_CALLBACKS` - Enable or disable asynchronous message delivery callbacks. (Default: `False`)

### Customisation

**Customising deserialisation** 

You can customize how Kafka messages are deserialized by overriding the process_kafka_message method in your spider class. 

This allows for handling custom message formats or data transformations.

```python
class CustomSpider(KafkaListeningSpider):
    def process_kafka_message(self, message, meta={}, headers={}):
        # Custom deserialization logic
        # Return URL, metadata or None if extraction fails
        pass
```

⚠️ *By default*, the spider method `process_kafka_message` expects a JSON payload or a string containing a valid url. If it's a JSON object, it expects `url` in the K/V pair.

**Customising Producer & Consumer settings**

You can customize producer and consumer settings by providing a dictionary of configuration options in your Scrapy settings under `SCRAPY_PRODUCER_CONFIG` and `SCRAPY_CONSUMER_CONFIG`.

```python
# Example SCRAPY_PRODUCER_CONFIG
SCRAPY_PRODUCER_CONFIG = {
    'compression.type': 'gzip',
    'request.timeout.ms': 5000
}

# Example SCRAPY_CONSUMER_CONFIG
SCRAPY_CONSUMER_CONFIG = {
    'fetch.wait.max.ms': 10,
    'max.poll.interval.ms': 600000,
    'auto.offset.reset': 'latest'
}
```