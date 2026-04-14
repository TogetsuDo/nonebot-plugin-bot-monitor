import time
from datetime import datetime

from nonebot import logger, require, on_notice, get_driver, on_command
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    NoticeEvent,
    MessageEvent,
    GroupMessageEvent,
)

require("nonebot_plugin_apscheduler")

from .config import plugin_config
from .bot_monitor import (
    offline_bots,
    handle_bot_connect,
    get_bot_status_info,
    handle_bot_disconnect,
)
from .mail_notifier import notify_bot_offline, handle_test_mail_command

__plugin_meta__ = PluginMetadata(
    name="Bot状态监控",
    description="监控 Bot 在线状态，检测 Bot 离线并发送邮件通知",
    usage=(
        f"{plugin_config.bot_monitor_cmd_bot_status}"
        " - 查询当前连接的 Bot 列表（仅超级用户）\n"
        f"{plugin_config.bot_monitor_cmd_test_mail}"
        " - 测试邮件发送功能（仅超级用户）"
    ),
    type="application",
    homepage="https://github.com/TogetsuDo/nonebot-plugin-bot-status",
    config=plugin_config.__class__,
    supported_adapters={"~onebot.v11"},
    extra={
        "version": "1.0.0",
    },
)

# 群组冷却（内存），key: group_id，value: 上次触发时间戳
_group_cooldowns: dict[int, float] = {}
_COOLDOWN_SECONDS = 10

offline_notice = on_notice(priority=5, block=False)
bot_status_cmd = on_command(
    plugin_config.bot_monitor_cmd_bot_status,
    permission=SUPERUSER,
    priority=5,
    block=True,
)
test_mail_cmd = on_command(
    plugin_config.bot_monitor_cmd_test_mail,
    permission=SUPERUSER,
    priority=5,
    block=True,
)

driver = get_driver()


@driver.on_startup
async def startup() -> None:
    logger.info("nonebot-plugin-bot-monitor is running")


@driver.on_bot_connect
async def _(bot: Bot) -> None:
    await handle_bot_connect(bot)


@driver.on_bot_disconnect
async def _(bot: Bot) -> None:
    await handle_bot_disconnect(bot)


@offline_notice.handle()
async def handle_bot_offline_events(event: NoticeEvent) -> None:
    """处理协议端上报的 bot 离线事件（NapCat / Lagrange）"""
    bot_id = 0
    offline_message = ""
    source = ""

    if event.notice_type == "bot_offline":  # NapCat
        bot_id = getattr(event, "user_id", 0)
        offline_message = getattr(event, "message", "")
        source = "napcat_event"
        logger.warning(f"NapCat Bot {bot_id} offline: {offline_message}")

    elif getattr(event, "sub_type", None) == "BotOfflineEvent":  # Lagrange
        bot_id = getattr(event, "self_id", getattr(event, "user_id", 0))
        offline_message = "Bot Offline"
        source = "lagrange_event"
        logger.warning(f"Lagrange Bot {bot_id} offline")

    if bot_id and source:
        from .bot_monitor import get_bot_nickname

        try:
            nickname = await get_bot_nickname(bot_id)
        except Exception:
            nickname = offline_bots.get(bot_id, {}).get("nickname", "Unknown Nickname")

        offline_bots[bot_id] = {
            "nickname": nickname,
            "offline_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
        }

        await notify_bot_offline(bot_id, nickname, offline_message)


@test_mail_cmd.handle()
async def _(bot: Bot, event: MessageEvent) -> None:
    await handle_test_mail_command(bot, event)


@bot_status_cmd.handle()
async def handle_bot_status(bot: Bot, event: MessageEvent) -> None:
    """查询所有 bot 的在线/离线状态"""
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
        last_time = _group_cooldowns.get(group_id, 0.0)
        if time.time() - last_time < _COOLDOWN_SECONDS:
            return
        _group_cooldowns[group_id] = time.time()

    online_bots, offline_bots_filtered = await get_bot_status_info()

    online_info = ""
    if online_bots:
        bot_list = [f"{nickname} ({bid})" for bid, nickname in online_bots.items()]
        online_info = f"在线的Bot (Total: {len(online_bots)}):\n" + "\n".join(bot_list)

    offline_info = ""
    if offline_bots_filtered:
        offline_list = [
            f"{nickname} ({bid})" for bid, nickname in offline_bots_filtered.items()
        ]
        offline_info = (
            f"\n\n离线的Bot (Total: {len(offline_bots_filtered)}):\n"
            + "\n".join(offline_list)
        )

    await bot_status_cmd.finish((online_info + offline_info) or "暂无 Bot 信息")
