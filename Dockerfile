FROM python:3.8.5-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 5050

CMD ["uvicorn",\
    "hello-nlp.main:app",\
    "--host", "0.0.0.0",\
    "--port", "5050"\
    ]
