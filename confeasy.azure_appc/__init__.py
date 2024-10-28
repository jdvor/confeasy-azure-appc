"""dd"""

from __future__ import annotations
from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AzureAppConfigurationClient
import os

__version__ = "0.0.1"


class AzureAppConfig:

    def __init__(self, client: AzureAppConfigurationClient, prefix: str | None = None) -> None:
        self._client = client
        self._prefix = prefix

    @classmethod
    def from_conn_str(cls, conn_str: str, prefix: str | None = None) -> AzureAppConfig:
        client = AzureAppConfigurationClient.from_connection_string(conn_str)
        return cls(client, prefix)

    @classmethod
    def from_conn_str_in_envars(cls, name: str, prefix: str | None = None) -> AzureAppConfig:
        conn_str = os.environ.get(name)
        if not conn_str:
            raise ValueError(f'environment variable {name} is not set')
        return cls.from_conn_str(conn_str, prefix)

    @classmethod
    def from_endpoint(cls, base_url: str, prefix: str | None = None) -> AzureAppConfig:
        credential = DefaultAzureCredential()
        # noinspection PyTypeChecker
        client = AzureAppConfigurationClient(base_url, credential)
        return cls(client, prefix)

    @classmethod
    def from_endpoint_in_envars(cls, name: str, prefix: str | None = None) -> AzureAppConfig:
        base_url = os.environ.get(name)
        if not base_url:
            raise ValueError(f'environment variable {name} is not set')
        return cls.from_endpoint(base_url, prefix)

    def get_configuration_data(self) -> dict[str, str | int | float | bool]:
        key_filter = None if self._prefix is None else f'{self._prefix}*'
        # noinspection PyTypeChecker
        idx = 0 if self._prefix is None else len(self._prefix)
        result = {}
        for kvp in self._client.list_configuration_settings(key_filter=key_filter):
            key = kvp.key[idx:] if idx > 0 else kvp.key
            value = kvp.value
            result[key] = value
        return result
