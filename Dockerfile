# Build stage
FROM python:3.13-alpine AS builder

WORKDIR /isort
COPY . .

RUN pip install --no-cache-dir uv

RUN SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0 uv build .

# Release stage
FROM python:3.13-alpine

# Install the wheel from the build stage
COPY --from=builder /isort/dist/ /tmp/
RUN \
    pip install --no-cache-dir /tmp/*.whl && \
    rm /tmp/*.whl

ENTRYPOINT ["isort"]
