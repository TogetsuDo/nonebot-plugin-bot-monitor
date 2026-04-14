import asyncio
from datetime import datetime, timedelta

from nonebot import logger, require, get_bots
from nonebot.adapters.onebot.v11 import Bot

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .config import plugin_config

# 已知的所有 bot id
known_bots: set[int] = set()
# 离线 bot 信息
offline_bots: dict[int, dict[str, str]] = {}


async def get_bot_nickname(bot_id: int, current_bots: dict | None = None) -> str:
    """获取 Bot 昵称"""
    nickname = "Unknown Nickname"
    try:
        bots = current_bots if current_bots is not None else get_bots()

        if str(bot_id) in bots:
            try:
                info = await bots[str(bot_id)].call_api(
                    "get_stranger_info", user_id=bot_id
                )
                nickname = info.get("nickname", "Unknown Nickname")
                if nickname != "Unknown Nickname":
                    return nickname
            except Exception as e:
                logger.debug(f"Failed to get bot {bot_id} info using itself: {e}")

        available_bots = [b for bid, b in bots.items() if int(bid) != bot_id]

        for attempt in range(3):
            if attempt > 0:
                logger.debug(
                    f"Retrying ({attempt + 1}/3) to get nickname for bot {bot_id}"
                )
            for bot_instance in available_bots:
                try:
                    info = await bot_instance.call_api(
                        "get_stranger_info", user_id=bot_id
                    )
                    nickname = info.get("nickname", "Unknown Nickname")
                    if nickname != "Unknown Nickname":
                        return nickname
                except Exception as e:
                    logger.debug(
                        f"Attempt {attempt + 1}: Failed using bot "
                        f"{bot_instance.self_id}: {e}"
                    )
            if attempt < 2:
                await asyncio.sleep(0.1)

    except Exception as e:
        logger.debug(f"Failed to get nickname for bot {bot_id}: {e}")

    return nickname


async def handle_bot_connect(bot: Bot) -> None:
    bot_id = int(bot.self_id)
    known_bots.add(bot_id)
    offline_bots.pop(bot_id, None)


async def handle_bot_disconnect(bot: Bot) -> None:
    bot_id = int(bot.self_id)
    if bot_id in offline_bots and "source" in offline_bots[bot_id]:
        return

    nickname = await get_bot_nickname(bot_id)
    offline_bots[bot_id] = {
        "nickname": nickname,
        "offline_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "disconnect_event",
    }

    job_id = f"bot_monitor_check_{bot_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    run_time = datetime.now() + timedelta(
        seconds=plugin_config.bot_monitor_offline_grace_time
    )
    scheduler.add_job(
        id=job_id,
        func=check_bot_still_offline,
        args=[bot_id, nickname],
        misfire_grace_time=60,
        coalesce=True,
        max_instances=1,
        trigger="date",
        run_date=run_time,
    )


async def check_bot_still_offline(bot_id: int, nickname: str) -> None:
    """宽限期结束后确认 bot 是否真的离线"""
    bots = get_bots()
    if str(bot_id) not in bots:
        logger.warning(f"Bot {bot_id} offline, sending notification")
        if bot_id in offline_bots:
            offline_bots[bot_id]["offline_time"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            offline_bots[bot_id] = {
                "nickname": nickname,
                "offline_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "checked_offline",
            }
        try:
            from .mail_notifier import notify_bot_offline

            await notify_bot_offline(bot_id, nickname)
        except Exception as e:
            logger.error(f"Failed to send offline notification for bot {bot_id}: {e}")
    else:
        if (
            bot_id in offline_bots
            and offline_bots[bot_id].get("source") == "checked_offline"
        ):
            del offline_bots[bot_id]


async def get_bot_status_info() -> tuple[dict[int, str], dict[int, str]]:
    """获取所有 bot 的在线/离线状态"""
    current_bots = get_bots()

    all_bot_ids: set[int] = set(known_bots)
    all_bot_ids.update(int(bid) for bid in current_bots.keys())
    all_bot_ids.update(offline_bots.keys())

    async def get_nickname_with_status(bot_id: int) -> tuple[int, str, bool]:
        if str(bot_id) in current_bots:
            nickname = await get_bot_nickname(bot_id, current_bots)
            return bot_id, nickname, True
        else:
            nickname = await get_bot_nickname(bot_id)
            if bot_id in offline_bots:
                offline_bots[bot_id]["nickname"] = nickname
            return bot_id, nickname, False

    results = await asyncio.gather(
        *[get_nickname_with_status(bid) for bid in all_bot_ids],
        return_exceptions=True,
    )

    online_bots: dict[int, str] = {}
    offline_bots_filtered: dict[int, str] = {}

    for result in results:
        if not isinstance(result, tuple):
            logger.warning(f"Error getting bot info: {result}")
            continue
        bot_id, nickname, is_online = result
        if is_online:
            online_bots[bot_id] = nickname
            if bot_id in offline_bots:
                offline_bots[bot_id]["nickname"] = nickname
        else:
            offline_bots_filtered[bot_id] = nickname

    return online_bots, offline_bots_filtered
