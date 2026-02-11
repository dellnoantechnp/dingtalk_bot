FROM --platform=$TARGETPLATFORM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1

# Set working directory
WORKDIR /dingtalk_bot

# Copy project files and requirements
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# -----------------------------
FROM --platform=$TARGETPLATFORM python:3.13-slim

LABEL org.opencontainers.image.base.name="docker.io/dellnoantechnp/dingtalk-bot:latest" \
      org.opencontainers.image.description="A CICD interactive message sender to DingTalk IM" \
      org.opencontainers.image.source="https://github.com/dellnoantechnp/dingtalk_bot" \
      org.opencontainers.image.title="dingtalk-bot"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /dingtalk_bot

## Port
# api
EXPOSE 8000
# metrics
EXPOSE 8100

COPY scripts/supervisord.conf /etc/supervisord.conf

# 拷贝 site-packages
COPY --from=builder /dingtalk_bot/.venv /dingtalk_bot/.venv
ENV PATH="/dingtalk_bot/.venv/bin:$PATH"

COPY . .

RUN rm -rf .git/

CMD supervisord