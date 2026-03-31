# PetClaw

PetClaw 是一个面向 `OpenClaw` 本地部署场景的桌面端 MVP 工具，基于 `PyQt6` 构建，用来降低用户在 Windows 环境下启动、隔离和加固 OpenClaw Docker 环境的操作门槛。

当前版本更偏向“本地引导器 + 安全辅助面板”，而不是替代 OpenClaw 本体。它的核心思路是：

- 检测本机 `Docker Desktop` 是否可用
- 引导用户选择 `OpenClaw` 根目录
- 复制官方 `docker compose` 命令，减少手敲命令出错
- 将工作目录拆分为输入只读、输出可写两类挂载
- 对 Gateway 端口进行本地回环绑定，降低暴露风险
- 为 `docker-compose.yml` 和 `.env` 提供备份与一键恢复能力

## MVP 目标

这个 MVP 主要验证三件事：

1. 用户能否以更低成本完成 OpenClaw 的本地初始化
2. 是否能在不重写 OpenClaw 官方流程的前提下，增加一层本地安全加固
3. GUI 引导 + 日志反馈的交互形式是否足够清晰

## 当前功能

### 1. 环境检测

- 自动轮询 `Docker Desktop` 状态
- 检查 OpenClaw Onboard 是否完成（通过 `.env` 判断）
- 检查 Gateway 是否已在本地端口上线

### 2. OpenClaw 启动引导

- 选择 `OpenClaw` 根目录
- 一键复制初始化命令：`docker compose up -d`
- 一键复制网关启动命令：`docker compose up -d openclaw-gateway`

### 3. 安全加固

- 将 Gateway 端口绑定到 `127.0.0.1`
- 向 `.env` 注入 `PETCLAW_INPUT_DIR` 与 `PETCLAW_OUTPUT_DIR`
- 重写 `docker-compose.yml` 中的工作区挂载逻辑
- 将挂载目录拆分为：
  - 输入目录：只读（RO）
  - 输出目录：读写（RW）
- 支持备份和一键恢复原始配置

### 4. 运行态辅助

- 检测并清理 OpenClaw 相关容器
- 保留本地操作日志
- 支持日志分页与清空

## 技术栈

- `Python`
- `PyQt6`
- `docker` Python SDK
- 本地 `Docker Desktop`

## 项目结构

```text
PetClaw/
├─ main.py
├─ modules/
│  ├─ container_manager.py
│  ├─ env_manager.py
│  ├─ logger_manager.py
│  ├─ port_manager.py
│  ├─ security_manager.py
│  ├─ volume_manager.py
│  └─ __init__.py
└─ petclaw_history.log
```

## 运行环境

建议环境：

- Windows 10/11
- Python 3.10+
- 已安装并启动 `Docker Desktop`
- 本地已有 `OpenClaw` 项目目录

## 安装依赖

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install PyQt6 docker
```

## 启动方式

```powershell
python main.py
```

## 推荐使用流程

1. 启动 `Docker Desktop`
2. 运行 `PetClaw`
3. 选择本地 `OpenClaw` 根目录
4. 点击复制 Onboard 命令，并在终端执行
5. 设置输入目录（RO）和输出目录（RW）
6. 执行路径变量注入
7. 执行 YAML 路径解耦
8. 执行端口安全加固
9. 复制 Gateway 启动命令并运行
10. 通过界面状态灯确认服务状态

## 设计说明

PetClaw 当前没有直接接管 OpenClaw 全部生命周期，而是采用“尽量兼容官方流程”的思路：

- 通过复制命令，让用户继续使用官方 `docker compose` 流程
- 通过修改 `.env` 和 `docker-compose.yml` 增加本地隔离能力
- 通过自动备份支持回滚，降低试错成本

这种方式对 MVP 来说更轻量，也更适合验证产品方向。

## 已知限制

- 当前依赖本机已安装 `Docker Desktop`
- 当前主要针对 Windows 使用习惯设计
- 依赖用户本地已有 OpenClaw 根目录
- 还没有打包为 `.exe`
- 还没有自动安装依赖、自动发现 OpenClaw 路径等增强能力

## 后续可扩展方向

- 本地配置记忆化，减少重复选择目录和重复配置操作
- OpenClaw 初始配置引导，进一步压缩首次使用门槛
- 完成初始配置后的一键启动能力，减少手动复制命令的步骤
- Agent 日志关联，让容器运行状态与任务日志更容易追踪
- 增加更完整的错误提示与诊断面板
- 增加 `.exe` 打包与安装器

## 演示截图

当前你已经有 4 张实验截图，建议后续统一放到：

```text
docs/screenshots/
```

推荐命名方式：

- `docs/screenshots/01-overview.png`
- `docs/screenshots/02-onboard.png`
- `docs/screenshots/03-security.png`
- `docs/screenshots/04-logs.png`

后续可以在这里补充：

- 主界面总览
- OpenClaw 初始化引导
- 安全加固区域
- 日志与运行状态区域

## 备注

这是一个用于验证产品方向的 MVP。当前重点是：

- 先把核心流程跑通
- 先把安全隔离思路验证清楚
- 先把交互路径整理成可展示、可继续迭代的版本

如果后续你希望，我可以继续帮你补：

- GitHub 仓库简介文案
- `requirements.txt`
- 发布版本说明模板
- 项目路线图（Roadmap）
- 中英双语 README
