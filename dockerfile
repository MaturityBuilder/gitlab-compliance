# -------------------------------
# Stage 1: Build with Poetry
# -------------------------------
FROM python:3.12.11-slim as builder

ENV POETRY_VERSION=1.8.2
WORKDIR /build

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy only Poetry files for caching
COPY pyproject.toml poetry.lock* ./

# Install only gitlab-docs (no dev dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the actual source code (in case `gitlab-docs` is local)
COPY . .

RUN rm -rf dist/* && poetry build

# -------------------------------
# Stage 2: Slim runtime
# -------------------------------
FROM python:3.12.11-slim as runtime

WORKDIR /app
# Copy installed site-packages and scripts from builder
COPY --from=builder /build/dist/* /app/
RUN pip3 install -q $(ls /app/*.tar.gz)

ENTRYPOINT ["gitlab-docs"]
