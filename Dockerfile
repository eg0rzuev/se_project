FROM python:3.11.2-slim-buster
ENV PATH "/root/.local/bin:$PATH"
COPY pyproject.toml ./
RUN apt-get update \
    && apt-get -y install libpq-dev=11.19-0+deb10u1 gcc git curl\
    && pip3 install --upgrade pip \
    && curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0 \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev
COPY app.py ./
COPY constants ./constants
COPY query_exec_funcs ./query_exec_funcs
CMD [ "python3", "-u", "./app.py" ]