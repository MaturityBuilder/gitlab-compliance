FROM python:3.12.13-alpine3.24 AS builder
RUN pip3 install -q poetry==2.1.3
RUN mkdir -p /build && mkdir -p /build/src
WORKDIR /build
COPY pyproject.toml poetry.lock README.md ./
COPY ./src ./src/
COPY ./docs ./docs/
RUN poetry install --without docs
RUN poetry build

FROM python:3.12.13-alpine3.24 AS gitlab-compliance
LABEL org.opencontainers.image.title="gitlab-compliance" \
      org.opencontainers.image.description="BDD compliance testing for GitLab CI/CD — by MaturityBuilder" \
      org.opencontainers.image.source="https://github.com/MaturityBuilder/gitlab-compliance" \
      org.opencontainers.image.vendor="MaturityBuilder" \
      org.opencontainers.image.url="https://maturitybuilder.github.io/gitlab-compliance/"
RUN mkdir -p /gitlab-compliance/
WORKDIR /gitlab-compliance
COPY --from=builder /build/dist/*.tar.gz .
RUN pip3 install --no-cache-dir -q $(ls *.tar.gz) && rm -rf build/dist/ && rm -rf *.tar.gz && pip3 cache purge && pip uninstall -y pip3
# Create a group and user
RUN addgroup -S app && adduser -S gitlab-compliance -G app
# Tell docker that all future commands should run as the gitlab-compliance user
USER gitlab-compliance

ENTRYPOINT ["gitlab-compliance"]
