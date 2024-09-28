FROM python:3.12

RUN pip install -q gitlab-docs

ENTRYPOINT ["gitlab-docs"]
# CMD entrypoint.py
