"""Config for launch celery"""
from celery import Celery
from celery_app.update_db import run_update_base
from celery_app.parser import ExcelParser
import asyncio


celery_instance = Celery(
    'periodic_task',
    broker=(f'amqp://guest:guest@'
            f'localhost:5672')
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
    parser = ExcelParser()
    parse_menu, parse_submenu, parse_dish = asyncio.run(parser.build_menu())
    asyncio.run(run_update_base(parse_menu, parse_submenu, parse_dish))
    return True
