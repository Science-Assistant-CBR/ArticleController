import os

from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker

from app.parsers.interfax import InterfaxParser
from app.parsers.president import PresidentParser
from app.parsers.rbc import RBCParser
from app.parsers.tass import TassParser
from app.parsers.ria import RIAParser

broker = ListQueueBroker(url=os.getenv("REDIS_URL", ""))
scheduler = TaskiqScheduler(broker, sources=(LabelScheduleSource(broker),))

proxies = ["http://mD43Dh:6HWR8m@168.196.241.114:8000"]


@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def parse_predisent():
    parser = PresidentParser(proxies=proxies)
    await parser.parse()


@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def parse_interfax():
    parser = InterfaxParser(proxies=proxies)
    await parser.parse()


@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def parse_rbc():
    parser = RBCParser(proxies=proxies)
    await parser.parse()


@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def parse_tass():
    parser = TassParser(proxies=proxies)
    await parser.parse()


@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def parse_ria():
    parser = RIAParser(proxies=proxies)
    await parser.parse()
