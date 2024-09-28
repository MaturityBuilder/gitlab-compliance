FROM python:3.12-slim
WORKDIR /gitlab-docs
RUN pip install -q gitlab-docs

ENTRYPOINT ["gitlab-docs"]
