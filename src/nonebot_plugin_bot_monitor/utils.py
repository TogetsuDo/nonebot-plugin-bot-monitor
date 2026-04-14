from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib
from nonebot import logger

from .config import MailConfig


async def send_mail(title: str, content: str, mail_config: MailConfig) -> str | None:
    """发送邮件通知，成功返回 None，失败返回错误信息"""
    message = MIMEMultipart("alternative")
    message["Subject"] = Header(title, "utf-8").encode()
    message["From"] = mail_config.user
    message["To"] = mail_config.notice_email
    message.attach(MIMEText(content))

    use_tls = mail_config.port == 465

    try:
        async with aiosmtplib.SMTP(
            hostname=mail_config.server, port=mail_config.port, use_tls=use_tls
        ) as smtp:
            await smtp.login(mail_config.user, mail_config.password)
            await smtp.send_message(message)
    except Exception as e:
        err = f"邮件发送失败：{e}"
        logger.error(err)
        return err

    logger.info("通知邮件发送成功!")
    return None
