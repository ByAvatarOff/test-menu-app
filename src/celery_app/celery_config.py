"""Config for launch celery"""
import asyncio

from celery import Celery
from sqlalchemy.exc import SQLAlchemyError

from celery_app.parser import ExcelParser
from celery_app.update_db import run_update_base
from config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_PORT, RABBITMQ_USER

celery_instance = Celery(
    'periodic_task',
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}'
)


celery_instance.conf.beat_schedule = {
    'periodic_task': {
        'task': 'celery_app.celery_config.update_base',
        'schedule': 15.0,
    },
}
celery_instance.conf.timezone = 'UTC'
celery_instance.autodiscover_tasks()


@celery_instance.task
def update_base():
    """Periodic task for update base use excel document"""
    try:
        parser = ExcelParser()
        parse_menu, parse_submenu, parse_dish = asyncio.run(parser.build_menu())
        asyncio.run(run_update_base(parse_menu, parse_submenu, parse_dish))
        return True
    except FileNotFoundError:
        return False
    except SQLAlchemyError:
        return False
