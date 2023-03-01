FROM python:3.11.2-slim-buster
COPY app.py ./
COPY constants ./constants
COPY query_exec_funcs ./query_exec_funcs
RUN apt-get update \
    && pip3 install pyTelegramBotAPI \
    && pip3 install psycopg2
CMD [ "python3", "-u", "./app.py" ]