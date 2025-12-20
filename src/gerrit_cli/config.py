"""Configuration management module"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from gerrit_cli.utils.exceptions import ConfigError


@dataclass
class GerritConfig:
    """Gerrit Configuration"""

    url: str
    username: str
    password: str

    @classmethod
    def from_env(cls) -> "GerritConfig":
        """Load configuration from environment variables

        Environment Variables:
            GERRIT_URL: Gerrit Server URL
            GERRIT_USERNAME: Username
            GERRIT_PASSWORD: Password (Preferred)
            GERRIT_TOKEN: HTTP Token (Alternative)

        Returns:
            GerritConfig: Configuration object

        Raises:
            ConfigError: Missing or invalid configuration
        """
        # Load .env file
        load_dotenv()

        url = os.getenv("GERRIT_URL")
        username = os.getenv("GERRIT_USERNAME")
        password = os.getenv("GERRIT_PASSWORD") or os.getenv("GERRIT_TOKEN")

        # Validate required config
        if not all([url, username, password]):
            missing = []
            if not url:
                missing.append("GERRIT_URL")
            if not username:
                missing.append("GERRIT_USERNAME")
            if not password:
                missing.append("GERRIT_PASSWORD or GERRIT_TOKEN")

            raise ConfigError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please set environment variables or create a .env file (see .env.example)"
            )

        config = cls(url=url, username=username, password=password)
        config.validate()
        return config

    def validate(self) -> None:
        """Validate configuration

        Raises:
            ConfigError: Invalid configuration
        """
        if not self.url.startswith(("http://", "https://")):
            raise ConfigError(f"GERRIT_URL must be a valid HTTP(S) URL, current value: {self.url}")

        # Remove trailing slash
        if self.url.endswith("/"):
            self.url = self.url.rstrip("/")
