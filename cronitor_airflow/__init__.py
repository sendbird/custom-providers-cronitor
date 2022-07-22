from enum import Enum


class CronNotification(Enum):
  DEFAULT = 'default'
  DP_CRON = 'dw-airflow-dp'
  MESG_SERVER = 'mesg-server'
  DASHBOARD_CRON = 'dashboard-cron'
  CALLS_PROD = 'calls_prod'


def get_provider_info():
  return {
    "package-name": "custom-providers-cronitor",
    "name": "Cronitor integration for Airflow",
    "description": 'Airflow plugin for Cronitor, with hook, operator',
    "connection-types": [
      {
        'connection-type': 'cronitor',
        'hook-class-name': "cronitor_airflow.hooks.cronitor_hook.CronitorHook"
      }
    ],
  }
