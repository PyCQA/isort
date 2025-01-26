ARG VERSION=3
FROM python:$VERSION

# Install pip and uv
RUN python -m pip install --upgrade pip && python -m pip install uv

# Setup as minimal a stub project as possible, simply to allow caching base dependencies
# between builds.
#
# If error is encountered in these steps, can safely be removed locally.
RUN mkdir -p /isort/isort
RUN mkdir -p /isort/tests
RUN touch /isort/isort/__init__.py
RUN touch /isort/tests/__init__.py
RUN touch /isort/README.md
WORKDIR /isort
COPY pyproject.toml uv.lock /isort/
RUN uv sync

# Install latest code for actual project
RUN rm -rf /isort
COPY . /isort
RUN uv sync

# Run full test suite
CMD /isort/scripts/test.sh
