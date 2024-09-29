FROM • python:3.12-slim
WORKDIR /gitlab-docs
RUN pip install -q gitlab-docs
RUN useradd -d /home/gitlab-docs -m -s /bin/bash gitlab-docs
USER gitlab-docs
ENTRYPOINT ["gitlab-docs"]
