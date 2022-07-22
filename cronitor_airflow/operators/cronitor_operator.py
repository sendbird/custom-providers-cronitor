from typing import Dict, List, Literal
import os

from airflow.models import BaseOperator
from airflow.utils.context import Context

from common.cronitor_airflow.hooks.cronitor_hook import CronitorHook


CronitorState = Literal["run", "complete", "fail", "ok"]


class CronitorOperator(BaseOperator):
  """
  This operator allows you to ping Cronitor to inform the monitor of the status of your DAG.

  :param state: Required. The status of the DAG. One of ["run", "complete", "fail", "ok"]
  :param cronitor_conn_id: The Cronitor connection name in Airflow. Defaults to 'cronitor_default'
  """

  def __init__(
    self,
    state: CronitorState,
    cronitor_conn_id: str = 'cronitor_default',
    **kwargs,
  ) -> None:
    super().__init__(**kwargs)
    self.state = state
    self.cronitor_conn_id = cronitor_conn_id
    self.kwargs = kwargs

  def _monitor_name(self, additional_tags: Dict[str, str], dag_id: str) -> str:
    # monitor_name should not exceed 100 characters
    prefix = f'dw-airflow-dag-'

    suffix = ''
    for tag in additional_tags:
      suffix += f'-{tag}:{additional_tags.get(tag).lower()}'

    available_len = 100 - len(prefix) - len(suffix)
    name = dag_id
    while len(name) > available_len:
      prev_name_len = len(name)
      name = name[name.find('_') + 1:]

      if prev_name_len == len(name):
        raise Exception('Name cannot be shrank more!')

    return f'{prefix}{name}{suffix}'

  def _tags(self, additional_tags: Dict[str, str]) -> List[str]:
    tags = []
    for tag in additional_tags:
      tags.append(f'{tag}:{additional_tags.get(tag)}')
    return tags

  def execute(self, context: Context) -> None:
    hook = CronitorHook(cronitor_conn_id='cronitor_default')
    default_args = self.kwargs['default_args']
    cronitor_supress_for = default_args.get('cronitor_supress_for', tuple('dev'))
    if os.getenv('ENV', 'dev') not in cronitor_supress_for and context.get('run_id', '').startswith('scheduled__'):
      execution_timeout = default_args.get('execution_timeout')

      additional_tags = default_args.get('cronitor_additional_tags', {})
      hook.get_monitor(
        monitor_name=self._monitor_name(additional_tags, context.get('dag').dag_id),
        schedule=context.get('dag').schedule_interval or 'every 24 hours',
        notify=default_args.get('cronitor_notify', CronNotification.DEFAULT.value),
        tags=self._tags(additional_tags),
        grace_seconds=default_args.get('cronitor_grace_seconds', 600),
        timeout=int(execution_timeout.total_seconds() / 60) if execution_timeout else None
      )

    if self.state == 'run':
      hook.run()
    elif self.state == 'complete':
      hook.complete()
    elif self.state == 'fail':
      hook.fail()
