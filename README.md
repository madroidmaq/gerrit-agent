# Gerrit CLI

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

### `gerrit change list`

列出 changes。

**选项：**
- `-q, --query TEXT`: 查询条件（默认: `status:open`）
- `-n, --limit INTEGER`: 返回结果数量（默认: 25）
- `-o, --owner TEXT`: 按所有者筛选（使用 `me` 表示当前用户）
- `-p, --project TEXT`: 按项目筛选
- `--format [table|json]`: 输出格式（默认: table）

### `gerrit change view`

查看 change 详情。

**参数：**
- `CHANGE_ID`: Change ID（可以是数字 ID、Change-Id 或完整路径）

**选项：**
- `--format [table|json]`: 输出格式（默认: table）
- `--comments`: 显示评论
- `--messages`: 显示消息历史
- `--files`: 显示文件列表

### `gerrit change comment`

添加评论到 change。

**参数：**
- `CHANGE_ID`: Change ID

**选项：**
- `-m, --message TEXT`: 评论内容
- `-f, --file PATH`: 从文件读取评论内容
- `--draft`: 保存为草稿（暂未实现）

### `gerrit review`

发送 review（打分+评论）。

**参数：**
- `CHANGE_ID`: Change ID

**选项：**
- `-m, --message TEXT`: Review 消息
- `--code-review [+2|+1|0|-1|-2]`: Code-Review 打分
- `--verified [+1|0|-1]`: Verified 打分
- `-f, --file PATH`: 从文件读取消息
- `--submit`: Review 后直接提交（暂未实现）

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
