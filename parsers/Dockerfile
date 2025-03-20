FROM python:3.12-slim

RUN apt-get update && \
  apt-get install -y locales && \
  sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
  dpkg-reconfigure --frontend=noninteractive locales

WORKDIR /app

COPY ./common/ /common
WORKDIR /app/

COPY ./parsers/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./parsers/app ./app
COPY ./parsers/run.sh .

EXPOSE 6379

ENV C_FORCE_ROOT=true
ENV PYTHONUNBUFFERED=1

#CMD ["ls", "app"]
#CMD ["sh", "-c", "taskiq", "scheduler", "tasks:scheduler", "&", "taskiq", "worker", "tasks:broker"]
#CMD ["taskiq", "scheduler", "tasks:scheduler"]
CMD ["sh", "run.sh"]
