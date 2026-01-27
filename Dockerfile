FROM --platform=$TARGETPLATFORM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_LINK_MODE=copy

# Set working directory
WORKDIR /dingtalk_bot

# Copy project files and requirements
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# -----------------------------
FROM --platform=$TARGETPLATFORM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /dingtalk_bot

# Install supervisord
RUN apt-get update \
 && apt-get install -y --no-install-recommends supervisor \
 && rm -rf /var/lib/apt/lists/*

# 拷贝 site-packages
COPY --from=builder /usr/local/lib/python3.13/site-packages \
                    /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY server_config/supervisord.conf /etc/supervisord.conf

## Port
# api
EXPOSE 8000
# metrics
EXPOSE 8100

COPY . .

CMD supervisord