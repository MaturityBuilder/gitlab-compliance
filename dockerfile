FROM python:3.12.11-slim AS builder
RUN pip3 install -q poetry==2.1.3
RUN mkdir -p /build && mkdir -p /build/src
WORKDIR /build
COPY pyproject.toml poetry.lock README.md ./
COPY ./src ./src/
copy ./docs ./docs/
RUN poetry install
RUN poetry build

FROM python:3.12.11-alpine AS gitlab-docs
RUN mkdir -p /gitlab-docs/
WORKDIR /gitlab-docs
COPY --from=builder build/dist/* .
RUN pip3 install -q $(ls *.tar.gz) && rm -rf *.tar.gz
RUN pip3 cache purge
# Create a group and user
RUN addgroup -S app && adduser -S gitlab-docs -G app
# Tell docker that all future commands should run as the gitlab-docs user
USER gitlab-docs

ENTRYPOINT ["gitlab-docs"]
