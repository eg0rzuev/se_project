FROM python:3.11.2-slim-buster
COPY app.py user_msgs.py ./
RUN apt-get update \
    && pip3 install pyTelegramBotAPI
CMD [ "python3", "-u", "./app.py" ]