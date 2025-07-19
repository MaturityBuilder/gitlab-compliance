FROM python:3.12-slim
WORKDIR /gitlab-docs
RUN mkdir -p dist
COPY dist/* dist/
# Disables installing from pypi instead the docker will copy in locally built package and install
# RUN pip install -q gitlab-docs
RUN pip3 install -q $(ls ./dist/*.tar.gz)
RUN rm -rf dist
RUN useradd -d /home/gitlab-docs -m -s /bin/bash gitlab-docs
# USER gitlab-docs
ENTRYPOINT ["gitlab-docs"]
