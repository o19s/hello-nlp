FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN python -m spacy download 'en_core_web_lg'
RUN python -m nltk.downloader wordnet

COPY . .

ENV PYTHONPATH=/app
EXPOSE 5055

CMD uvicorn hello_nlp.main:app --host 0.0.0.0 --port $PORT --use-colors --access-log --env-file $CONFIG_FILE