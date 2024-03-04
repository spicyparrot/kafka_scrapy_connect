import os
from setuptools import setup, find_packages

MY_DIR = os.path.dirname(__file__)
README_MD = open(os.path.join(MY_DIR, 'README.md')).read()

setup(
    name='kafka-scrapy-connect',
    version='{{VERSION_PLACEHOLDER}}',
    description='Integrating Scrapy with kafka using the confluent-kafka python client',
    long_description=README_MD,
    long_description_content_type="text/markdown",
    packages=['kafka_scrapy_connect'],
    install_requires=[
        'scrapy >= 2.11.1',
        'confluent-kafka >= 2.2.0'
    ],
    url='https://github.com/spicyparrot/kafka_scrapy_connect',
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
    keywords="kafka, scrapy, crawling, scraping",
)
