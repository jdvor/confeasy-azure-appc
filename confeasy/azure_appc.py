"""Module containing Azure AppConfiguration configuration source."""

from __future__ import annotations
from azure.appconfiguration import AzureAppConfigurationClient
import os
import re

__version__ = "0.0.1"

SNAKE_CASE_REPLACE_PATTERN = re.compile(r"(?<!^)(?=[A-Z][a-z]|[A-Z](?=[A-Z][a-z]|$))")


class AzureAppConfig:
    """Azure AppConfiguration configuration source."""

    def __init__(
        self,
        client: AzureAppConfigurationClient,
        prefix: str | None = None,
        label: str | None = None) -> None:
        self._client = client
        self._prefix = prefix
        self._label = label

    @classmethod
    def from_conn_str(cls, conn_str: str, prefix: str | None = None, label: str | None = None) -> AzureAppConfig:
        client = AzureAppConfigurationClient.from_connection_string(conn_str)
        return cls(client, prefix, label)

    @classmethod
    def from_conn_str_in_envars(cls, name: str, prefix: str | None = None, label: str | None = None) -> AzureAppConfig:
        conn_str = os.environ.get(name)
        if not conn_str:
            raise ValueError(f'environment variable {name} is not set')
        return cls.from_conn_str(conn_str, prefix, label)

    def get_configuration_data(self) -> dict[str, str | int | float | bool]:
        """
        Get data which should be merged into configuration.
        The keys should follow the required pattern - see documentation in developer.md.
        """
        key_filter = None if self._prefix is None \
            else f"{self._prefix}*" if not self._prefix.endswith("*") \
            else self._prefix
        # noinspection PyTypeChecker
        idx = 0 if self._prefix is None else len(self._prefix)
        result: dict[str, str] = {}
        for kvp in self._client.list_configuration_settings(key_filter=key_filter, label_filter=self._label):
            key = kvp.key[idx:].lstrip(".") if idx > 0 else kvp.key
            key = SNAKE_CASE_REPLACE_PATTERN.sub("_", key).lower()
            value = kvp.value
            result[key] = value
        return result
