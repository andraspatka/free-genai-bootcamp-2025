FROM python:3.12

WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt && pip install watchfiles debugpy

COPY app /app

# Expose the debug port
EXPOSE 5678

CMD ["watchfiles", "python main.py", "/app"]