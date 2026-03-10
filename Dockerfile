FROM python:3.13

WORKDIR /isort
COPY pyproject.toml uv.lock /isort/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.0 /uv /uvx /bin/

# Setup as minimal a stub project as possible, simply to allow caching base dependencies
# between builds.
#
# If error is encountered in these steps, can safely be removed locally.
RUN mkdir -p /isort/isort
RUN mkdir -p /isort/tests
RUN touch /isort/isort/__init__.py
RUN touch /isort/tests/__init__.py
RUN touch /isort/README.md
COPY . /isort
RUN SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0 uv sync --all-extras --frozen

# Install latest code for actual project
RUN rm -rf /isort

# Run full test suite
CMD /isort/scripts/test.sh
