FROM python:3.12-slim

WORKDIR /app

COPY acontroller ./acontroller

RUN pip install -r acontroller/requirements.txt

CMD ["uvicorn", "acontroller.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
