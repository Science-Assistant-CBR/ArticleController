FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY acontroller/ ./acontroller/

COPY common/ ./acontroller/

RUN pip install --no-cache-dir -r ./acontroller/requirements.txt

CMD ["uvicorn", "acontroller.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
