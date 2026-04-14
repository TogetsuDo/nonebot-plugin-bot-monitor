from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    # 邮件推送配置
    bot_monitor_smtp_user: str = ""
    bot_monitor_smtp_password: str = ""
    bot_monitor_smtp_server: str = ""
    bot_monitor_smtp_port: int = 465
    bot_monitor_notice_email: str = ""
    # 离线等待时长（秒），在此时间内重连则不发送通知
    bot_monitor_offline_grace_time: int = 30
    # 额外通知邮箱列表
    bot_monitor_admin_emails: list[str] = []
    # 自定义命令名
    bot_monitor_cmd_bot_status: str = "Bot在吗"
    bot_monitor_cmd_test_mail: str = "测试邮件"


class MailConfig:
    def __init__(
        self, user: str, password: str, server: str, port: int, notice_email: str
    ):
        self.user = user
        self.password = password
        self.server = server
        self.port = port
        self.notice_email = notice_email

    def check_params(self) -> bool:
        """检查邮件参数是否填写完整"""
        return bool(
            self.user
            and self.password
            and self.server
            and self.port
            and self.notice_email
        )


plugin_config = get_plugin_config(Config)
