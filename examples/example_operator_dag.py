from airflow import DAG
from datetime import timedelta, datetime
from cronitor_airflow.operators.cronitor_operator import CronitorOperator
from cronitor_airflow import CronNotification
import time
from airflow.operators.python import PythonOperator
import random

with DAG(
  'test_succeed',
  description='this is a test dag',
  schedule_interval='0 0 * * *',
  catchup=False,
  default_args={
    'execution_timeout': timedelta(minutes=30),
    'cronitor_notify': CronNotification.DP_CRON.value,
    'cronitor_additional_tags': {
      'team': 'dp',
      'env': 'dev',
    }
  },
  start_date=datetime(2022, 4, 15)
) as dag:
  start = CronitorOperator(
    task_id='cronitor-start',
    state='run',
  )


  def wait():
    time.sleep(4)
    if random.randint(1, 10) > 5:
      # Randomly cause an error
      raise Exception()
    else:
      pass


  wait_a_bit = PythonOperator(task_id='wait', python_callable=wait)

  end_success = CronitorOperator(
    task_id='cronitor-end-succeed',
    state='complete',
    trigger_rule='all_success',
  )

  end_failure = CronitorOperator(
    task_id='cronitor-end-failure',
    state='fail',
    trigger_rule='one_failed',
  )

  start >> wait_a_bit >> [end_success, end_failure]
