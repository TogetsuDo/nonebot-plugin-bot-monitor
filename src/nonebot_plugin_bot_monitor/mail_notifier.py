from datetime import datetime

from nonebot import logger

from .utils import send_mail
from .config import MailConfig, plugin_config


async def notify_bot_offline(
    bot_id: int, nickname: str, offline_reason: str = ""
) -> None:
    """发送 bot 离线通知邮件"""
    mail_config = MailConfig(
        user=plugin_config.bot_monitor_smtp_user,
        password=plugin_config.bot_monitor_smtp_password,
        server=plugin_config.bot_monitor_smtp_server,
        port=plugin_config.bot_monitor_smtp_port,
        notice_email=plugin_config.bot_monitor_notice_email,
    )

    if not mail_config.check_params():
        logger.warning(
            "Mail configuration incomplete, cannot send offline notification"
        )
        return

    title = f"[Bot 离线] {nickname} 已离线"
    reason_info = f"离线原因: {offline_reason}\n\n" if offline_reason else ""
    content = (
        f"{reason_info}"
        f"Bot 昵称：{nickname}\n"
        f"Bot 账号：{bot_id}\n"
        f"掉线时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    result = await send_mail(title, content, mail_config)
    if result:
        logger.error(f"Failed to send offline notification mail: {result}")
    else:
        logger.info(f"Offline notification mail sent for bot {bot_id}")

    for email in plugin_config.bot_monitor_admin_emails:
        try:
            admin_config = MailConfig(
                user=plugin_config.bot_monitor_smtp_user,
                password=plugin_config.bot_monitor_smtp_password,
                server=plugin_config.bot_monitor_smtp_server,
                port=plugin_config.bot_monitor_smtp_port,
                notice_email=email,
            )
            result = await send_mail(title, content, admin_config)
            if result:
                logger.error(f"Failed to send mail to {email}: {result}")
            else:
                logger.info(f"Offline notification sent to {email} for bot {bot_id}")
        except Exception as e:
            logger.error(f"Exception sending mail to {email}: {e}")


async def handle_test_mail_command(bot, event) -> None:
    """处理测试邮件命令"""
    from nonebot.matcher import Matcher

    mail_config = MailConfig(
        user=plugin_config.bot_monitor_smtp_user,
        password=plugin_config.bot_monitor_smtp_password,
        server=plugin_config.bot_monitor_smtp_server,
        port=plugin_config.bot_monitor_smtp_port,
        notice_email=plugin_config.bot_monitor_notice_email,
    )

    if not mail_config.check_params():
        missing: list[str] = []
        if not plugin_config.bot_monitor_smtp_user:
            missing.append("bot_monitor_smtp_user")
        if not plugin_config.bot_monitor_smtp_password:
            missing.append("bot_monitor_smtp_password")
        if not plugin_config.bot_monitor_smtp_server:
            missing.append("bot_monitor_smtp_server")
        if not plugin_config.bot_monitor_notice_email:
            missing.append("bot_monitor_notice_email")
        await Matcher().finish(f"邮箱配置缺少参数: {', '.join(missing)}")
        return

    title = "[Test] 这是一封测试邮件"
    content = (
        f"Bot 在吗？\n\n"
        f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Bot ID: {bot.self_id}\n\n"
        f"如果你收到了这封邮件，证明邮箱配置正确。"
    )

    result = await send_mail(title, content, mail_config)
    matcher = Matcher()
    if result:
        await matcher.finish(f"测试邮件发送失败: {result}")
    else:
        await matcher.finish("测试邮件发送成功！")
