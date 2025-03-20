FROM python:3.12-slim AS build-image

RUN python -m venv /opt/venv

# set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1
ENV LD_LIBRARY_PATH="/opt/bb/lib64"
ENV PKG_CONFIG_PATH="/opt/bb/lib64/pkgconfig"
ENV PYTHONPATH=/code/

# install dependencies
COPY ./common/ /common
WORKDIR /code/

COPY ./backend/requirements.txt .

RUN pip install --upgrade --no-cache-dir pip && \
  pip install --no-cache-dir -r requirements.txt

COPY ./backend/alembic alembic
COPY ./backend/alembic.ini alembic.ini
COPY ./backend/app /code/app
COPY ./backend/app/config /code/app/config

COPY ./backend/run.sh /code/run.sh
RUN chmod +x /code/run.sh
CMD ["sh", "/code/run.sh"]
