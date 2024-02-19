import os
from setuptools import setup, find_packages

MY_DIR = os.path.dirname(__file__)
LONG_DESC = open(os.path.join(MY_DIR, 'README.rst')).read()

setup(
    name='kafka-scrapy-connect',
    version='1.0.0',
    description='Integrating Scrapy with kafka using confluent-kafka lib',
    #long_description=LONG_DESC,
    packages=['kafka_scrapy_connect'],
    install_requires=[
        'scrapy >= 2.11.1',
        'confluent-kafka >= 2.2.0'
    ],
)
