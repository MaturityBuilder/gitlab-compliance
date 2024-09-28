FROM python:3.13.0b4-alpine3.20
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY ca-certs.pem /usr/local/share/ca-certificates/my-cert.crt
RUN cat /usr/local/share/ca-certificates/my-cert.crt >> /etc/ssl/certs/ca-certificates.crt && \
    apk --no-cache add \
        curl
RUN pip install gitlab-docs
# # import sys
# from pathlib import Path
# import oyaml as yaml
# from prettytable import PrettyTable
# from loremipsum import get_sentences
# import argparse
# RUN pip install pyyaml \
#     pytablewriter \
#     oyaml \
#     prettytable loremipsum \
#     markdown-analysis \
#     semver
# RUN mkdir -p /gitlab-docs
# WORKDIR /gitlab-docs
# COPY src/ .

ENTRYPOINT ["gitlab-docs"]
# CMD entrypoint.py