# PetClaw 上传 GitHub 完整流程

这份文档适合当前这个 `PetClaw` MVP 项目，用于把本地代码整理后上传到 GitHub，并保证仓库页面看起来完整、专业、可继续迭代。

## 一、上传前先整理什么

在上传前，建议你先确认以下几件事：

### 1. 保留应该上传的内容

建议上传：

- `main.py`
- `modules/`
- `README.md`
- `.gitignore`
- `docs/github-upload-guide.md`

### 2. 不要上传的内容

建议不要上传：

- `__pycache__/`
- 本地日志文件，如 `petclaw_history.log`
- 虚拟环境目录，如 `.venv/`
- 个人 IDE 配置，如 `.vscode/`、`.idea/`
- 本地生成的 `.env`、备份文件或敏感配置

### 3. 先检查仓库目录是否干净

如果目录下存在缓存或日志，可以先手动删除，或者让 `.gitignore` 忽略它们。

## 二、建议的仓库命名

建议 GitHub 仓库名使用：

- `PetClaw`
- `petclaw`
- `petclaw-mvp`

如果你希望突出它和 OpenClaw 的关系，也可以用：

- `petclaw-for-openclaw`

## 三、在本地初始化 Git

在项目根目录打开 PowerShell，执行：

```powershell
git init
git add .
git commit -m "init: first MVP version of PetClaw"
```

如果你还没有配置 Git 用户信息，先执行：

```powershell
git config --global user.name "你的 GitHub 名称"
git config --global user.email "你的 GitHub 邮箱"
```

## 四、在 GitHub 创建远程仓库

1. 登录 GitHub
2. 点击右上角 `New repository`
3. 仓库名称填写你要使用的名称，例如 `PetClaw`
4. 选择 `Public` 或 `Private`
5. 不要勾选自动创建 `README`、`.gitignore` 或 `LICENSE`
6. 点击 `Create repository`

创建完成后，GitHub 会给你一段远程仓库地址，例如：

```text
https://github.com/your-name/PetClaw.git
```

## 五、把本地项目推送到 GitHub

在本地项目根目录执行：

```powershell
git branch -M main
git remote add origin https://github.com/your-name/PetClaw.git
git push -u origin main
```

如果你后续继续更新，常用流程是：

```powershell
git add .
git commit -m "feat: update MVP interaction"
git push
```

## 六、首次上传后建议立刻做的事

### 1. 完善仓库简介

GitHub 仓库右侧 About 建议填写：

**Description：**

```text
A PyQt6-based desktop MVP for guiding, isolating and hardening local OpenClaw Docker workflows.
```

**Website：**

如果暂时没有官网，可以留空。

**Topics：**

建议添加：

- `python`
- `pyqt6`
- `docker`
- `desktop-app`
- `mvp`
- `openclaw`
- `security`

### 2. 检查 README 展示效果

上传后，重点确认：

- 标题是否清晰
- 项目定位是否一眼能看懂
- 安装和运行命令是否可直接复制
- 功能列表是否足够完整

### 3. 补截图

对于 GUI 项目，建议尽快补充 1~3 张截图：

- 主界面总览
- 安全加固区域
- 日志区域

截图可以放到：

```text
docs/screenshots/
```

然后在 `README.md` 中引用。

## 七、推荐的提交信息规范

你后续迭代时，建议用这种提交格式：

```text
feat: add gateway hardening workflow
fix: repair env injection logic
docs: refine README and upload guide
refactor: simplify container manager logic
```

## 八、适合这个 MVP 的版本发布节奏

可以按下面方式打版本：

- `v0.1.0`：可运行的最小 MVP
- `v0.2.0`：补充 README、截图、流程文档
- `v0.3.0`：加入 exe 打包或安装器
- `v0.4.0`：加入更自动化的 OpenClaw 集成

创建标签示例：

```powershell
git tag v0.1.0
git push origin v0.1.0
```

## 九、当前这个项目建议的 GitHub 展示重点

因为 `PetClaw` 还是 MVP，所以仓库页面最重要的是把下面三件事讲清楚：

1. 这是做什么的
2. 它解决了什么具体问题
3. 现在已经能跑到什么程度

建议你在 README 的开头就强调：

- 它是 `OpenClaw` 的本地部署辅助工具
- 它重点解决安全隔离与启动引导问题
- 它目前是 MVP，目标是先验证产品方向

## 十、一个最稳妥的实际上传顺序

建议你按下面顺序操作：

1. 先检查 `.gitignore` 是否正确
2. 先确认 `README.md` 已可用
3. 本地执行 `git init`
4. 本地执行第一次 `commit`
5. 在 GitHub 创建空仓库
6. 添加远程地址并 `push`
7. 打开仓库页面检查展示效果
8. 再补充截图、仓库简介和 topics

## 十一、如果你想让仓库看起来更完整

下一步建议优先补这些文件：

- `requirements.txt`
- `LICENSE`
- `CHANGELOG.md`
- `docs/screenshots/`

其中最优先的是：

1. `requirements.txt`
2. GUI 截图
3. 首个 Release 说明

## 十二、常见问题

### 1. 我已经在 GitHub 新建了 README，怎么办？

如果远程仓库不是空仓库，第一次推送时可能会冲突。最简单的处理方式是：

- 删除远程自动生成的内容重新建空仓库
- 或者先 `pull` 再处理合并

对于第一次上传本地 MVP，推荐直接新建空仓库。

### 2. 日志文件要不要传？

不建议。日志更适合作为本地运行产物，不适合进入版本库。

### 3. `__pycache__` 要不要传？

不要。这类文件应该由 `.gitignore` 排除。

### 4. 现在没有截图，可以先上传吗？

可以。先保证代码、README 和流程文档完整，截图后补即可。

## 十三、一套可直接复制的命令

把下面命令中的 GitHub 地址换成你自己的：

```powershell
git init
git add .
git commit -m "init: first MVP version of PetClaw"
git branch -M main
git remote add origin https://github.com/your-name/PetClaw.git
git push -u origin main
```

到这里，你的 MVP 就已经可以完整上传到 GitHub 了。
