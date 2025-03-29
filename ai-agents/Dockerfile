FROM python:3.12

WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt && pip install watchfiles

COPY app /app

CMD ["watchfiles", "python main.py", "/app"]