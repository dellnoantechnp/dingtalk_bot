# dingtalk-bot

[English description](./README.md)

一个向钉钉即时通讯推送 CICD 交互消息的机器人服务。

## 项目简介

本项目是一个基于 Django 的服务，集成了钉钉（DingTalk）和 Argo Workflows，将 CI/CD 流水线的实时状态更新以互动卡片的形式推送到钉钉群聊中。用户可以与这些卡片进行交互（审批/拒绝），并实时查看工作流进度的更新。

## 架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Argo       │────▶│  dingtalk-   │────▶│  钉钉 IM         │
│  Workflows  │     │  bot         │     │  （互动卡片）     │
│             │◀────│  (Django)    │◀────│                  │
└─────────────┘     └──────┬───────┘     └──────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Redis      │
                    │ (消息队列 +  │
                    │  缓存)       │
                    └──────────────┘
```

**核心组件：**

- **Django Web 应用** — REST API 端点，用于接收工作流通知和管理卡片生命周期。
- **Celery Worker** — 异步任务队列，用于获取工作流状态、创建/更新钉钉卡片以及轮询更新。
- **钉钉 Stream 服务** — 长连接 WebSocket，用于接收钉钉的实时回调（按钮点击等）。
- **Argo Workflows 集成** — 查询 Argo API 获取流水线执行状态、节点详情和输出参数（CHANGE_LOG、CI_ENVIRONMENT_NAME）。
- **Prometheus 指标** — 在 8100 端口暴露应用监控指标。

## 功能特性

- 创建展示 CICD 流水线状态的钉钉互动卡片
- 随工作流进展自动更新卡片内容（按可配置的时间间隔轮询）
- 支持审批/拒绝互动按钮，按用户追踪投票状态
- 解析并渲染 Git 提交日志到卡片 Markdown 内容中
- 基于 Redis 的卡片状态持久化存储
- 健康检查端点（`/health/live`、`/health/ready`）

## 项目结构

```
dingtalk_bot/
├── core/                        # 核心工具（Redis 客户端、日志过滤器）
├── customRobot/                 # 自定义机器人处理器及 API 接口视图
├── dingtalk/                    # 钉钉集成
│   ├── services/                # Argo Workflows 服务、钉钉客户端、Stream 服务
│   ├── tasks/                   # Celery 任务（工作流轮询、卡片更新）
│   └── Models/                  # 卡片和请求的 Pydantic 模型
├── dingtalk_stream_service/     # Stream 守护进程管理命令
├── health/                      # 健康检查视图及 Django health-check 集成
├── utils/                       # 共享工具（Markdown 模板、耗时计算）
└── scripts/                     # 启动脚本（run.sh、supervisord.conf）
```

## 环境变量

| 变量名 | 默认值 | 说明 |
|---|---|---|
| `DINGTALK_CLIENT_ID` | — | 钉钉应用 Client ID |
| `DINGTALK_CLIENT_SECRET` | — | 钉钉应用 Client Secret |
| `DINGTALK_ROBOT_CODE` | — | 钉钉机器人 code |
| `REDIS_HOST` | `127.0.0.1` | Redis 主机地址 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `REDIS_DB` | `0` | Redis 数据库编号 |
| `REDIS_PASSWORD` | `""` | Redis 密码 |
| `ARGO_WORKFLOWS_DOMAIN` | `https://workflows.example.com` | Argo Workflows API 域名 |
| `ARGO_WORKFLOWS_TOKEN` | `undefined` | Argo Workflows API 令牌 |
| `ARGO_WORKFLOWS_WORKER_NAMESPACE` | `Undefined_workflows_task_namespace` | Argo 工作流命名空间 |
| `UPDATE_INTERVAL_SECONDS` | `20` | 卡片更新轮询间隔（秒） |
| `DJANGO_DEBUG` | `False` | Django 调试模式 |
| `PROMETHEUS_METRICS_EXPORT_PORT` | `8100` | Prometheus 指标端口 |

## 本地运行

### 前置条件

- Python 3.13+
- Redis 服务器
- uv（包管理器）

### 安装与配置

```bash
# 安装依赖
uv sync

# 设置环境变量
export DINGTALK_CLIENT_ID=your_client_id
export DINGTALK_CLIENT_SECRET=your_client_secret
export REDIS_HOST=localhost
export ARGO_WORKFLOWS_DOMAIN=https://your-argo-domain
export ARGO_WORKFLOWS_TOKEN=your_token

# 执行数据库迁移（如需要）
python manage.py migrate

# 启动 Web 服务
python manage.py runserver 0.0.0.0:8000

# 在另一个终端中，启动 Celery Worker
celery -A dingtalk worker --loglevel INFO -P eventlet

# 在另一个终端中，启动钉钉 Stream 服务
python manage.py run_dingtalk_stream
```

## Docker 部署

```bash
docker build -t dingtalk-bot .
docker run -d \
  -p 8000:8000 \
  -p 8100:8100 \
  --env-file .env \
  dingtalk-bot
```

容器通过 supervisord 运行三个进程：
- **main** — Django 开发服务器，端口 8000
- **callback-stream** — 钉钉 Stream 回调监听器
- **celery** — Celery 异步任务 Worker

## API 端点

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/customRobot/newNotification` | 触发新的 CICD 卡片通知（Celery 异步任务） |
| `GET`  | `/customRobot/workflowTest` | 测试 Argo Workflows 集成 |
| `GET`  | `/health/live` | 存活探针（检查 Redis 连接性） |
| `GET`  | `/metrics` | Prometheus 监控指标 |

## Celery 任务

| 任务名 | 说明 |
|---|---|
| `create_and_update_card` | 创建钉钉卡片并开始监控工作流状态 |
| `fetch_task_info` | 获取 Argo 工作流任务详情 |
| `monitor_workflow_status` | 轮询工作流状态并按配置间隔更新卡片 |

## License

MIT
