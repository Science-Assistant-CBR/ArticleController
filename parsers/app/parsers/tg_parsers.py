import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import emoji
import telethon
from dotenv import dotenv_values
from telethon import TelegramClient

from common.common.schemas import News

config = dotenv_values(".env")

api_id = int(config['api_id'])
api_hash = config['api_hash']
password = config['password']
phone = config['phone']

channels = (
    'test_cb_parser',
    'banksta',
    'Tapor_news',
    'rbc_news',
    'forbesrussia',
    'Sanctions_Inspector'
)


async def parse_news(client, last_time) -> (list, dict):
    """
    :returns all news from a given time for all tg channels
    """
    parsed_news = []

    for channel in channels:
        news = await retrieve_news(client, channel, last_time)

        formatted_news = []
        for raw_new in news:
            formatted_news.append(await format_new(raw_new, channel))

        parsed_news.extend(formatted_news)

    return parsed_news


async def retrieve_news(client, channel: str, last_time: datetime):
    """
    :returns all news in common format from a channel, time of last new + 1 sec
    """
    news = []
    try:
        async for new in client.iter_messages(channel, offset_date=last_time, reverse=True):
            news.append(new)
    except telethon.errors.RPCError as e:
        print(f"Error fetching messages from {channel}: {e}")
        return []

    news = [new for new in news if new.text != '']

    return news


async def format_new(new, channel):
    """
    TODO: 1 Delete emojis, telegram chars, links
    TODO: 2 Add LLM to handle augmented metadata
    """
    an = await augment_new_metadata(new)
    ct = await cleaned_text(new)

    formatted_new: News = News(
        publication_datetime=new.date,
        url=f'https://t.me/{channel}/{new.id}',
        text=ct,
        source_name=channel,
        tags=an['tags'],
        persons=an['persons'],
        news_id=str(new.id),
        title=an['title'],
        topic=an['topic'],
    )
    return formatted_new


async def cleaned_text(new):
    text = new.text
    clean_text = emoji.replace_emoji(text, replace='')
    return clean_text


async def augment_new_metadata(new):
    """
    TODO: LLM should derive it but for now it will be NONE
    """

    analysed_new_md = {
        'tags': None,
        'persons': None,
        'title': None,
        'topic': None
    }
    return analysed_new_md


async def get_last_time_from_server(file_name="news_log.txt"):
    """
    TODO: Add real server functionality
    """
    latest_time = None
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("publication_datetime="):
                    timestamp = line.split("=", 1)[1].strip()
                    try:
                        current_time = datetime.fromisoformat(timestamp)
                        if not latest_time or current_time > latest_time:
                            latest_time = current_time
                    except ValueError:
                        print(f"Invalid datetime format: {timestamp}")
                        continue

        if latest_time is None:
            print("No valid entries found, defaulting to 10 minutes ago")
            return datetime.now(ZoneInfo("UTC")) - timedelta(minutes=10)
        print(latest_time)
        return latest_time + timedelta(seconds=1)

    except FileNotFoundError:
        print(f"{file_name} not found, defaulting to 10 minutes ago")
        with open(file_name, "w", encoding="utf-8"):
            pass
        return datetime.now(ZoneInfo("UTC")) - timedelta(minutes=10)
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        return datetime.now(ZoneInfo("UTC")) - timedelta(minutes=10)


async def send_news(news, file_name="news_log.txt"):
    """
    TODO: Add real server functionality
    """
    try:
        with open(file_name, "a", encoding="utf-8") as file:
            for new in news:
                file.write(f"publication_datetime={new.publication_datetime.isoformat()}\n")
                file.write(f"url={new.url}\n")
                file.write(f"text={new.text}\n")
                file.write(f"source_name={new.source_name}\n")
                file.write(f"news_id={new.news_id}\n")
                file.write(f"tags={','.join(new.tags) if new.tags else 'None'}\n")
                file.write(f"persons={','.join(new.persons) if new.persons else 'None'}\n")
                file.write(f"title={new.title if new.title else 'None'}\n")
                file.write(f"topic={new.topic if new.topic else 'None'}\n")
                file.write("\n")
    except Exception as e:
        print(f"Error writing to {file_name}: {e}")


async def main():
    client = TelegramClient("m_session", api_id, api_hash)
    await client.start(phone=phone, password=password)
    last_time = await get_last_time_from_server()  #
    news = await parse_news(client, last_time)
    await send_news(news)  #


if __name__ == '__main__':
    asyncio.run(main())
