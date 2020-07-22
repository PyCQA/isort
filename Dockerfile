ARG VERSION=3
FROM python:$VERSION

RUN mkdir /isort
WORKDIR /isort

COPY pyproject.toml poetry.lock /isort/
RUN python -m pip install --upgrade pip && python -m pip install poetry && poetry install

COPY . /isort/
RUN poetry install

CMD /isort/scripts/test.sh
