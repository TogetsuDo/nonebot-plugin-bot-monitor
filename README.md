<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

## ✨ nonebot-plugin-bot-monitor ✨
[![LICENSE](https://img.shields.io/github/license/TogetsuDo/nonebot-plugin-bot-monitor.svg)](./LICENSE)
[![pypi](https://img.shields.io/pypi/v/nonebot-plugin-bot-monitor.svg)](https://pypi.python.org/pypi/nonebot-plugin-bot-monitor)
[![python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org)
[![uv](https://img.shields.io/badge/package%20manager-uv-black?style=flat-square&logo=uv)](https://github.com/astral-sh/uv)
<br/>
[![ruff](https://img.shields.io/badge/code%20style-ruff-black?style=flat-square&logo=ruff)](https://github.com/astral-sh/ruff)
[![pre-commit](https://results.pre-commit.ci/badge/github/TogetsuDo/nonebot-plugin-bot-monitor/master.svg)](https://results.pre-commit.ci/latest/github/TogetsuDo/nonebot-plugin-bot-monitor/master)

</div>

## 📖 介绍

NoneBot2 插件：监控 Bot 在线状态，检测 Bot 离线并发送邮件通知。


## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-bot-monitor --upgrade

使用 **pypi** 源安装

    nb plugin install nonebot-plugin-bot-monitor --upgrade -i "https://pypi.org/simple"

使用**清华源**安装

    nb plugin install nonebot-plugin-bot-monitor --upgrade -i "https://pypi.tuna.tsinghua.edu.cn/simple"

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details open>
<summary>uv</summary>

    uv add nonebot-plugin-bot-monitor

安装仓库 master 分支

    uv add git+https://github.com/TogetsuDo/nonebot-plugin-bot-monitor@master

</details>

<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-bot-monitor

安装仓库 master 分支

    pdm add git+https://github.com/TogetsuDo/nonebot-plugin-bot-monitor@master

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-bot-monitor

安装仓库 master 分支

    poetry add git+https://github.com/TogetsuDo/nonebot-plugin-bot-monitor@master

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_bot_monitor"]

</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中添加以下配置：

| 配置项 | 必填 | 默认值 | 说明 |
| :---: | :---: | :---: | :--- |
| `BOT_monitor_SMTP_USER` | 否 | 无 | SMTP 发件人账号 |
| `BOT_monitor_SMTP_PASSWORD` | 否 | 无 | SMTP 授权码（非登录密码） |
| `BOT_monitor_SMTP_SERVER` | 否 | 无 | SMTP 服务器地址 |
| `BOT_monitor_SMTP_PORT` | 否 | `465` | SMTP 端口，465 使用 SSL，其他端口使用 STARTTLS |
| `BOT_monitor_NOTICE_EMAIL` | 否 | 无 | 接收离线通知的邮箱 |
| `BOT_monitor_OFFLINE_GRACE_TIME` | 否 | `30` | 离线宽限期（秒），Bot 在此时间内重连则不发送通知 |
| `BOT_monitor_ADMIN_EMAILS` | 否 | `[]` | 额外通知邮箱列表，离线时同时通知这些邮箱 |
| `BOT_monitor_CMD_BOT_status` | 否 | `Bot在吗` | 查询 Bot 状态的命令名 |
| `BOT_monitor_CMD_TEST_MAIL` | 否 | `测试邮件` | 测试邮件发送的命令名 |

```dotenv
BOT_monitor_SMTP_USER=your@email.com
BOT_monitor_SMTP_PASSWORD=your_auth_code
BOT_monitor_SMTP_SERVER=smtp.example.com
BOT_monitor_SMTP_PORT=465
BOT_monitor_NOTICE_EMAIL=receiver@email.com
BOT_monitor_OFFLINE_GRACE_TIME=30
BOT_monitor_ADMIN_EMAILS=["admin1@qq.com", "admin2@qq.com"]

# 可选：自定义命令名
BOT_monitor_CMD_BOT_status=Bot在吗
BOT_monitor_CMD_TEST_MAIL=测试邮件
```

> 邮箱配置请参考各邮件服务商的 SMTP 设置说明（QQ 邮箱、163 邮箱等均需使用授权码而非登录密码）。

## 🎉 使用

> **无需任何插件配置即可使用 `Bot在吗` 命令**，只需在 `.env` 中设置 NoneBot2 的超级用户：
> ```dotenv
> SUPERUSERS=["你的QQ号"]
> ```
> 邮件通知功能才需要额外配置 `BOT_monitor_SMTP_*` 相关项。

以下命令仅 `SUPERUSERS` 可用：

| 指令 | 权限 | 需要@ | 范围 | 说明 |
| :---: | :---: | :---: | :---: | :--- |
| `Bot在吗`（可自定义） | 超级用户 | 否 | 群聊/私聊 | 查询所有 Bot 的在线/离线状态 |
| `测试邮件`（可自定义） | 超级用户 | 否 | 群聊/私聊 | 向配置的邮箱发送测试邮件，验证邮件配置是否正确 |

## 依赖

- [nonebot2](https://github.com/nonebot/nonebot2) >= 2.4.0
- [nonebot-adapter-onebot](https://github.com/nonebot/adapter-onebot) >= 2.4.0
- [nonebot-plugin-apscheduler](https://github.com/nonebot/plugin-apscheduler) >= 0.5.0
- [aiosmtplib](https://github.com/cole/aiosmtplib) >= 5.0.0

## License

MIT
