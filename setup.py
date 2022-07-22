from setuptools import setup

setup(
  name='custom-providers-cronitor',
  version='0.0.2',
  packages=['cronitor_airflow',
            'cronitor_airflow.operators',
            'cronitor_airflow.hooks'],
  install_requires=[
    "apache-airflow>=2.0.0",
    "cronitor>=4.5.0",
  ],
  url='https://github.com/sendbird/custom-providers-cronitor',
  author='SendBird Engineering team',
  author_email='platform@sendbird.com',
  description='Airflow plugin for Cronitor, with hook, operator,',
  entry_points={
    "apache_airflow_provider": ["provider_info = cronitor_airflow:get_provider_info"],
  },
  classifiers=[
    "Framework :: Apache Airflow",
    "Framework :: Apache Airflow :: Provider",
  ]
)
