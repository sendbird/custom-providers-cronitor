from typing import Dict, List
import logging

from airflow.hooks.base import BaseHook
import cronitor


log = logging.getLogger(__name__)


class DummyMonitor(object):
  def ping(self, state):
    log.info(f'DummyMonitor.{state}')
    return True


class CronitorHook(BaseHook):
  """
  Hook to manage connection to the Cronitor API
  """

  conn_name_attr = 'cronitor_conn_id'
  default_conn_name = 'cronitor_default'
  conn_type = 'cronitor'
  hook_name = 'Cronitor'

  @staticmethod
  def get_ui_field_behaviour() -> Dict:
    return {
      "hidden_fields": [
        "host", "schema", "login", "port", "extra",
      ],
      "relabeling": {
        "password": "Cronitor API Key",
      },
      "placeholders": {
        "password": "Your Cronitor API Key",
      }
    }

  def __init__(self, cronitor_conn_id: str = "cronitor_default"):
    self.cronitor_conn_id = cronitor_conn_id
    self.monitor = DummyMonitor()

  def get_monitor(self, monitor_name: str, schedule: str, notify: str, tags: List[str], grace_seconds: int,
                  timeout: int = None) -> None:
    connection = self.get_connection(self.cronitor_conn_id)
    cronitor.api_key = connection.password

    monitor_config = {
      'type': 'job',
      'key': monitor_name,
      'schedule': schedule,
      'notify': [
        notify
      ],
      'tags': tags,
      'grace_seconds': grace_seconds,
    }
    if timeout:
      monitor_config['assertions'] = [f'metric.duration < {timeout} min']

    try:
      monitor = cronitor.Monitor.put(
        [monitor_config]
      )
      log.info(f'Cronitor initialized: monitor name: {monitor_name}')
    except Exception as e:
      log.error(f'Fail to create/update cronitor monitor: [{monitor_name}]: ' + repr(e))
      raise
    self.monitor = monitor

  def run(self) -> None:
    if not self.monitor:
      log.warning(f'No valid cronitor monitor being found for: {self.monitor_name}')
    if not self.monitor.ping(state='run'):
      log.error('Cronitor job monitoring ping (run) failed')

  def complete(self) -> None:
    if not self.monitor:
      log.warning(f'No valid cronitor monitor being found for: {self.monitor_name}')
    if not self.monitor.ping(state='complete'):
      log.error('Cronitor job monitoring ping (complete) failed')

  def fail(self) -> None:
    if not self.monitor:
      log.warning(f'No valid cronitor monitor being found for: {self.monitor_name}')
    if not self.monitor.ping(state='fail'):
      log.error('Cronitor job monitoring ping (fail) failed')
