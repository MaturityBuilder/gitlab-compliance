FROM charlieasmith93/poetry-python3:3.12.12-1.8.3-dev AS builder
RUN mkdir -p /build && mkdir -p /build/src
WORKDIR /build
COPY pyproject.toml poetry.lock README.md ./
COPY ./src ./src/
COPY ./docs ./docs/
RUN poetry install -q
RUN poetry build

##############
# Final image
##############
FROM python:3.12-alpine AS alpine

# Harden defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN mkdir -p /gitlab-docs/
WORKDIR /gitlab-docs
COPY --from=builder build/dist/* .
RUN apk update -q && \
    apk upgrade -q
RUN pip install -q --no-cache-dir --upgrade pip==25.3 && \
    pip3 install --no-cache-dir -q $(ls *.tar.gz) && \
    rm -rf *.tar.gz

ENTRYPOINT ["gitlab-docs"]
CMD ["gitlab-docs", "--help"]

FROM python:3.12-slim AS slim
RUN mkdir -p /gitlab-docs/
WORKDIR /gitlab-docs
COPY --from=builder build/dist/* .
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -q --upgrade pip==25.3 && \
    pip3 install --no-cache-dir -q $(ls *.tar.gz) && rm -rf *.tar.gz
# Create a group and user
# Non-root user
RUN groupadd -r gitlab-docs && useradd -r -g gitlab-docs -s /usr/sbin/nologin gitlab-docs
USER gitlab-docs

WORKDIR /gitlab-docs
# Tell docker that all future commands should run as the gitlab-docs user
USER gitlab-docs

ENTRYPOINT ["gitlab-docs"]
