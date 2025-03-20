# News parsers 

need to use the schema from common directory, example:
```python
from common.schemas import News


news_item = News(
    publication_datetime="2024-11-26T10:00:00",
    url="https://example.com/news/12345",
    text="Важная новость о событиях в мире.",
    source_name="Example News",
    tags=["Политика", "Экономика"],
    persons=["Иванов", "Петров"],
    news_id="12345",
    title="События дня",
    topic="Политика"
)

print(news_item.json(indent=4))
```
