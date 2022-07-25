from airflow import DAG
from datetime import timedelta, datetime
from cronitor_airflow.operators.cronitor_operator import CronitorOperator
from cronitor_airflow import CronNotification
import time
from airflow.operators.python import PythonOperator
import random

"""
possible cronitor related default_args
:param cronitor_suppress_for: env in which cronitor alert should be suppressed for.
default) tuple('dev')
e.g) ('dev', 'stg') or tuple('dev')
:param cronitor_notify: alert notified through this notification.
default) CronNotification.DEFAULT.value (dummy notification)
e.g) CronNotification.DP_CRON.value
:param cronitor_additional_tags: tags are created for the monitor and these tags are concatenated to the monitor name.
default) {}
e.g) {'team': 'dp', 'env': 'stg'} 
:param cronitor_grace_seconds: the monitor can wait this much seconds before it triggers the actual alert.
default) 600
e.g) 1200
:param execution_timeout:
default) None
e.g) timedelta(minutes=10)

monitor name is inferred from the name of the dag_id and additional_tags.
For example, if dag_id is test_succeed and additional_tags are {'team': 'dp', 'env': 'dev'} then
name will be `dw-airflow-dag-test_succeed-team:dp-env:dev`.
"""
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
  """
  task_id and state are required.
  possible states the following:
    run
    complete
    fail
    ok
  """
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
