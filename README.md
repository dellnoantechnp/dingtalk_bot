# dingtalk-bot

[中文说明](./README-cn.md)


A CICD interactive card message sender to DingTalk IM.

## Overview

This project is a Django-based service that integrates with DingTalk (钉钉) and Argo Workflows to deliver real-time CI/CD pipeline status updates as interactive cards in DingTalk group chats. Users can interact with these cards (approve/reject) and watch the workflow progress update live.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Argo       │────▶│  dingtalk-   │────▶│  DingTalk IM     │
│  Workflows  │     │  bot         │     │  (Interactive    │
│             │◀────│  (Django)    │◀────│   Cards)         │
└─────────────┘     └──────┬───────┘     └──────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Redis      │
                    │ (Broker +    │
                    │  Cache)      │
                    └──────────────┘
```

**Key components:**

- **Django Web App** — REST API endpoints for receiving workflow notifications and managing card lifecycle.
- **Celery Worker** — Async task queue for fetching workflow status, creating/updating DingTalk cards, and polling updates.
- **DingTalk Stream Service** — Long-lived WebSocket connection to receive real-time callbacks from DingTalk (button clicks, etc.).
- **Argo Workflows Integration** — Queries Argo API to get pipeline execution status, node details, and output parameters (CHANGE_LOG, CI_ENVIRONMENT_NAME).
- **Prometheus Metrics** — Exposes application metrics on port 8100.

## Features

- Create DingTalk interactive cards with CICD pipeline status
- Auto-update cards as workflow progresses (polling at configurable intervals)
- Interactive approve/reject buttons with per-user vote tracking
- Parse and render Git commit logs into card markdown content
- Persistent card state storage via Redis
- Health check endpoints (`/health/live`, `/health/ready`)

## Project Structure

```
dingtalk_bot/
├── core/                  # Core utilities (Redis client, log filters)
├── customRobot/           # Custom robot handlers & API interface views
├── dingtalk/              # DingTalk integration
│   ├── services/          # Argo Workflows service, DingTalk client, Stream service
│   ├── tasks/             # Celery tasks (workflow polling, card updates)
│   └── Models/            # Pydantic models for cards and requests
├── dingtalk_stream_service/  # Stream daemon management command
├── health/                # Health check views and Django health-check integration
├── utils/                 # Shared utilities (markdown templates, elapsed time)
└── scripts/               # Entry scripts (run.sh, supervisord.conf)
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DINGTALK_CLIENT_ID` | — | DingTalk app Client ID |
| `DINGTALK_CLIENT_SECRET` | — | DingTalk app Client Secret |
| `DINGTALK_ROBOT_CODE` | — | DingTalk robot code |
| `REDIS_HOST` | `127.0.0.1` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database number |
| `REDIS_PASSWORD` | `""` | Redis password |
| `ARGO_WORKFLOWS_DOMAIN` | `https://workflows.example.com` | Argo Workflows API domain |
| `ARGO_WORKFLOWS_TOKEN` | `undefined` | Argo Workflows API token |
| `ARGO_WORKFLOWS_WORKER_NAMESPACE` | `Undefined_workflows_task_namespace` | Argo workflow namespace |
| `UPDATE_INTERVAL_SECONDS` | `20` | Polling interval for card updates (seconds) |
| `DJANGO_DEBUG` | `False` | Django debug mode |
| `PROMETHEUS_METRICS_EXPORT_PORT` | `8100` | Prometheus metrics port |

## Running Locally

### Prerequisites

- Python 3.13+
- Redis server
- uv (package manager)

### Setup

```bash
# Install dependencies
uv sync

# Set environment variables
export DINGTALK_CLIENT_ID=your_client_id
export DINGTALK_CLIENT_SECRET=your_client_secret
export REDIS_HOST=localhost
export ARGO_WORKFLOWS_DOMAIN=https://your-argo-domain
export ARGO_WORKFLOWS_TOKEN=your_token

# Run migrations (if needed)
python manage.py migrate

# Start the web server
python manage.py runserver 0.0.0.0:8000

# In another terminal, start Celery worker
celery -A dingtalk worker --loglevel INFO -P eventlet

# In another terminal, start DingTalk Stream service
python manage.py run_dingtalk_stream
```

## Running with Docker

```bash
docker build -t dingtalk-bot .
docker run -d \
  -p 8000:8000 \
  -p 8100:8100 \
  --env-file .env \
  dingtalk-bot
```

The container runs three processes via supervisord:
- **main** — Django development server on port 8000
- **callback-stream** — DingTalk Stream callback listener
- **celery** — Celery worker for async tasks

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/customRobot/newNotification` | Trigger a new CICD card notification (Celery task) |
| `GET`  | `/customRobot/workflowTest` | Test Argo Workflows integration |
| `GET`  | `/health/live` | Liveness probe (checks Redis connectivity) |
| `GET`  | `/metrics` | Prometheus metrics |

## Celery Tasks

| Task | Description |
|---|---|
| `create_and_update_card` | Create a DingTalk card and start monitoring workflow status |
| `fetch_task_info` | Fetch Argo workflow task details |
| `monitor_workflow_status` | Poll workflow status and update card at configured intervals |

## License

MIT
