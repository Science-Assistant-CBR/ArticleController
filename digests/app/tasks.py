import os

from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker

broker = ListQueueBroker(url=os.getenv("REDIS_URL", ""))
scheduler = TaskiqScheduler(broker, sources=(LabelScheduleSource(broker),))


@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def create_digest():
    pass
