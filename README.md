查看当前项目中内容，根据 readme 中的内容新建# Gerrit CLI

Gerrit Code Review 的命令行工具，参考 GitHub CLI 的设计理念，让你可以通过命令行高效地进行代码审查。

## 特性

- 🔍 查看和搜索 Changes
- 💬 添加评论和 Review
- ⭐ Code-Review 和 Verified 打分
- 📊 美观的表格输出（使用 rich 库）
- 📄 支持 JSON 格式输出
- ⚙️ 简单的环境变量配置

## 安装

### 使用 uv（推荐）

```bash
# Clone 项目
git clone <repository-url>
cd gerrit-cli

# 安装依赖
uv sync

# 使用 uv run 运行
uv run gerrit --help
```

### 使用 pip

```bash
# Clone 项目
git clone <repository-url>
cd gerrit-cli

# 安装
pip install -e .

# 直接使用
gerrit --help
```

## 配置

Gerrit CLI 使用环境变量进行配置。你可以通过以下两种方式配置：

### 方式 1：环境变量

```bash
export GERRIT_URL=https://gerrit.example.com
export GERRIT_USERNAME=your_username
export GERRIT_PASSWORD=your_password
```

### 方式 2：.env 文件（推荐）

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# Gerrit 服务器配置
GERRIT_URL=https://gerrit.example.com
GERRIT_USERNAME=your_username
GERRIT_PASSWORD=your_password

# 或使用 HTTP Token（在 Gerrit Settings -> HTTP Credentials 生成）
# GERRIT_TOKEN=your_http_token
```

## 使用

### 查看帮助

```bash
gerrit --help
gerrit change --help
gerrit review --help
```

### 列出 Changes

```bash
# 列出所有 open 的 changes
gerrit change list

# 列出自己的 changes
gerrit change list --owner me

# 按项目筛选
gerrit change list --project myproject

# 自定义查询
gerrit change list -q "status:merged branch:main"

# 限制结果数量
gerrit change list -n 50

# JSON 格式输出
gerrit change list --format json
```

### 查看 Change 详情

```bash
# 查看 change 详情（使用数字 ID）
gerrit change view 12345

# 查看 change 详情（使用 Change-Id）
gerrit change view I1234567890abcdef

# 显示评论
gerrit change view 12345 --comments

# JSON 格式输出
gerrit change view 12345 --format json
```

### 拉取 Change 到本地

```bash
# 拉取 change 到本地新分支进行测试或审查
gerrit change fetch 12345

# 指定自定义分支名称
gerrit change fetch 12345 -b my-review-branch

# 如果分支已存在，强制删除并重新创建
gerrit change fetch 12345 --force

# 只拉取不切换分支（保持在当前分支）
gerrit change fetch 12345 --no-checkout

# 自动 stash 未提交的修改
gerrit change fetch 12345 --stash

# 不使用 stash，强制继续（可能丢失修改）
gerrit change fetch 12345 --no-stash
```

**处理未提交的修改：**

fetch 命令会检查工作区状态，如果有未提交的修改，会提供以下选项：

1. **使用 stash 保存（推荐）**：自动执行 `git stash`，在拉取完成后可以使用 `git stash pop` 恢复
2. **取消操作**：让你先手动处理当前修改
3. **强制继续**：直接切换分支（可能丢失未提交的修改）

你也可以使用 `--stash` 或 `--no-stash` 选项跳过询问。

**仓库验证：**

fetch 命令会智能检查当前仓库是否与 Change 匹配：

1. **不在 Git 仓库中**：会提示你需要 cd 到 Git 仓库目录
2. **没有 origin remote**：会警告并询问是否继续
3. **仓库与 Change 项目不匹配**：会警告并提供建议，防止在错误的仓库中拉取代码

这些检查确保你不会在错误的目录或仓库中执行 fetch 操作。

### 添加评论

```bash
# 添加评论
gerrit change comment 12345 -m "LGTM"

# 从文件读取评论
gerrit change comment 12345 -f comment.txt
```

### 发送 Review

```bash
# Code-Review +2
gerrit review 12345 --code-review +2 -m "Looks good to me!"

# Code-Review -1 with message
gerrit review 12345 --code-review -1 -m "需要修改以下问题..."

# Code-Review +2 and Verified +1
gerrit review 12345 --code-review +2 --verified +1 -m "LGTM and verified"

# 从文件读取 review 消息
gerrit review 12345 --code-review +2 -f review.txt
```

## 命令参考

Gerrit CLI 提供了完善的内置帮助文档。要查看所有可用命令和选项的详细说明，请直接运行：

```bash
# 查看所有命令
gerrit --help

# 查看特定命令的参数（例如 list）
gerrit change list --help
```

## Gerrit API 查询语法

`-q/--query` 选项支持 Gerrit 的查询语法。常用查询条件：

- `status:open` - 开放的 changes
- `status:merged` - 已合并的 changes
- `status:abandoned` - 已废弃的 changes
- `owner:username` - 按所有者筛选
- `owner:me` - 当前用户的 changes
- `project:projectname` - 按项目筛选
- `branch:branchname` - 按分支筛选
- `is:watched` - 正在关注的 changes
- `is:reviewer` - 作为 reviewer 的 changes

可以组合多个条件：

```bash
gerrit change list -q "status:open project:myproject branch:main"
```

## 开发

### 安装开发依赖

```bash
uv sync --extra dev
```

### 运行测试

```bash
uv run pytest
```

### 代码格式化

```bash
uv run black src/ tests/
uv run ruff check src/ tests/
```

### 类型检查

```bash
uv run mypy src/
```

## 项目结构

```
gerrit-cli/
├── src/gerrit_cli/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              # CLI 主入口
│   ├── config.py           # 配置管理
│   ├── client/
│   │   ├── api.py          # Gerrit API 客户端
│   │   ├── auth.py         # 认证处理
│   │   └── models.py       # 数据模型
│   ├── commands/
│   │   ├── change.py       # change 命令组
│   │   └── review.py       # review 命令
│   ├── formatters/
│   │   ├── base.py         # 格式化器基类
│   │   ├── table.py        # 表格格式化
│   │   └── json.py         # JSON 格式化
│   └── utils/
│       ├── exceptions.py   # 自定义异常
│       └── helpers.py      # 辅助函数
└── tests/                  # 测试文件
```

## 技术栈

- **CLI 框架**: [Click](https://click.palletsprojects.com/)
- **HTTP 客户端**: [httpx](https://www.python-httpx.org/)
- **数据验证**: [Pydantic](https://docs.pydantic.dev/)
- **输出格式化**: [Rich](https://rich.readthedocs.io/)
- **配置管理**: [python-dotenv](https://github.com/theskumar/python-dotenv)
- **项目管理**: [uv](https://docs.astral.sh/uv/)

## 待实现功能

- [ ] 草稿评论功能
- [ ] Submit change 功能
- [ ] 内联评论（针对特定代码行）
- [ ] 文件级别的 diff 查看
- [ ] Reviewer 管理
- [ ] 批量操作
- [ ] 配置文件支持（~/.gerrit-cli.yaml）
- [ ] 命令自动补全
- [ ] 支持拉取 Relation Chain（依赖链）
- [ ] 支持拉取指定的 Patch Set

## 常见问题

### 认证失败

确保你的用户名和密码正确。推荐使用 Gerrit 的 HTTP Token 而不是账户密码。

生成 HTTP Token:
1. 登录 Gerrit
2. 访问 Settings -> HTTP Credentials
3. 点击 "GENERATE NEW PASSWORD"
4. 将生成的 token 设置为 `GERRIT_TOKEN` 环境变量

### 网络超时

如果你的 Gerrit 服务器响应较慢，可能会遇到超时问题。当前超时设置为 30 秒，如需调整，请修改 `src/gerrit_cli/client/api.py` 中的 `timeout` 参数。

### 查询语法错误

确保查询条件符合 Gerrit 的查询语法。可以参考 [Gerrit 官方文档](https://gerrit-review.googlesource.com/Documentation/user-search.html)。

## 参考资源

- [Gerrit REST API 文档](https://gerrit-review.googlesource.com/Documentation/rest-api.html)
- [Gerrit Changes API](https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html)
- [GitHub CLI](https://cli.github.com/) - 设计灵感来源

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
