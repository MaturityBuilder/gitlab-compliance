FROM python:3.14.8-alpine3.24@sha256:f6a589d43c42b9e7f7dc67a12d37132491f362859a5d750607710cc56da3bc72 AS builder
RUN pip3 install -q poetry==2.5.1
RUN mkdir -p /build && mkdir -p /build/src
WORKDIR /build
COPY pyproject.toml poetry.lock README.md ./
COPY ./src ./src/
COPY ./docs ./docs/
RUN poetry install --without docs
RUN poetry build

FROM python:3.14.8-alpine3.24@sha256:f6a589d43c42b9e7f7dc67a12d37132491f362859a5d750607710cc56da3bc72 AS gitlab-compliance
LABEL org.opencontainers.image.title="gitlab-compliance" \
      org.opencontainers.image.description="BDD compliance testing for GitLab CI/CD — by MaturityBuilder" \
      org.opencontainers.image.source="https://github.com/MaturityBuilder/gitlab-compliance" \
      org.opencontainers.image.vendor="MaturityBuilder" \
      org.opencontainers.image.url="https://maturitybuilder.github.io/gitlab-compliance/"
RUN apk upgrade --no-cache
RUN mkdir -p /gitlab-compliance/
WORKDIR /gitlab-compliance
COPY --from=builder /build/dist/*.tar.gz .
RUN pip3 install --no-cache-dir -q $(ls *.tar.gz) \
    && rm -rf build/dist/ \
    && rm -rf *.tar.gz \
    && pip3 cache purge \
    && pip uninstall -y pip
# Create a group and user
RUN addgroup -S app && adduser -S gitlab-compliance -G app
# Tell docker that all future commands should run as the gitlab-compliance user
USER gitlab-compliance

ENTRYPOINT ["gitlab-compliance"]
