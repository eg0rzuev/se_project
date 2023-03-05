FROM python:3.11.2-slim-buster
RUN apt-get update \
    && apt-get -y install libpq-dev gcc git\
    && pip3 install --upgrade pip \
    && pip3 install pyTelegramBotAPI \
    && pip3 install psycopg2
COPY app.py ./
COPY constants ./constants
COPY query_exec_funcs ./query_exec_funcs
CMD [ "python3", "-u", "./app.py" ]