FROM python:3.12-slim

RUN apt-get update && \
  apt-get install -y locales texlive-luatex && \
  sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
  dpkg-reconfigure --frontend=noninteractive locales

WORKDIR /app

COPY ./common/ /common
WORKDIR /app/

COPY ./digests/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./digests/app ./app

EXPOSE 6379

ENV C_FORCE_ROOT=true
ENV PYTHONUNBUFFERED=1

CMD ["python3", "app/main.py"]
