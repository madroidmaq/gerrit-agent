"""配置管理模块"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from gerrit_cli.utils.exceptions import ConfigError


@dataclass
class GerritConfig:
    """Gerrit 配置"""

    url: str
    username: str
    password: str

    @classmethod
    def from_env(cls) -> "GerritConfig":
        """从环境变量加载配置

        环境变量:
            GERRIT_URL: Gerrit 服务器 URL
            GERRIT_USERNAME: 用户名
            GERRIT_PASSWORD: 密码（优先）
            GERRIT_TOKEN: HTTP Token（备选）

        Returns:
            GerritConfig: 配置对象

        Raises:
            ConfigError: 配置缺失或无效
        """
        # 加载 .env 文件
        load_dotenv()

        url = os.getenv("GERRIT_URL")
        username = os.getenv("GERRIT_USERNAME")
        password = os.getenv("GERRIT_PASSWORD") or os.getenv("GERRIT_TOKEN")

        # 验证必要配置
        if not all([url, username, password]):
            missing = []
            if not url:
                missing.append("GERRIT_URL")
            if not username:
                missing.append("GERRIT_USERNAME")
            if not password:
                missing.append("GERRIT_PASSWORD or GERRIT_TOKEN")

            raise ConfigError(
                f"缺少必要的环境变量配置: {', '.join(missing)}\n"
                f"请设置环境变量或创建 .env 文件（参考 .env.example）"
            )

        config = cls(url=url, username=username, password=password)
        config.validate()
        return config

    def validate(self) -> None:
        """验证配置有效性

        Raises:
            ConfigError: 配置无效
        """
        if not self.url.startswith(("http://", "https://")):
            raise ConfigError(f"GERRIT_URL 必须是有效的 HTTP(S) URL，当前值: {self.url}")

        # 移除 URL 末尾的斜杠
        if self.url.endswith("/"):
            self.url = self.url.rstrip("/")
