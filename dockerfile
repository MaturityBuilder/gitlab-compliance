FROM python:3.12-slim

# RUN pip install -q gitlab-docs

ENTRYPOINT ["gitlab-docs"]
