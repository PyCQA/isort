ARG VERSION=3
FROM python:$VERSION

RUN mkdir /isort
WORKDIR /isort
COPY . /isort

RUN python3 -m pip install poetry && poetry install

CMD /isort/scripts/done.sh
