"""Module containing Azure AppConfiguration configuration source."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re

from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import KeyVaultSecret, SecretClient


__version__ = "0.0.1"

SNAKE_CASE_REPLACE_PATTERN = re.compile(r"(?<!^)(?=[A-Z][a-z]|[A-Z](?=[A-Z][a-z]|$))")
KEYVAULT_REF_TYPE = "application/vnd.microsoft.appconfig.keyvaultref+json"


class AzureAppConfig:
    """Azure AppConfiguration configuration source."""

    def __init__(
        self, client: AzureAppConfigurationClient, prefix: str | None = None, label: str | None = None
    ) -> None:
        self._client = client
        self._prefix = prefix
        self._label = label
        self._allow_reading_keyvault_refs: bool = False
        self._secret_client_factory: Callable[[str], SecretClient] | None = None
        self._skip_on_error: bool = True

    @classmethod
    def from_conn_str_in_envars(cls, name: str, prefix: str | None = None, label: str | None = None) -> AzureAppConfig:
        """Create AzureAppConfig from a connection string that is expected at given environment variable."""
        conn_str = os.environ.get(name)
        if not conn_str:
            raise ValueError(f"environment variable {name} is not set")
        client = AzureAppConfigurationClient.from_connection_string(conn_str)
        return cls(client, prefix, label)

    def allow_reading_keyvault_references(
        self,
        client_factory: Callable[[str], SecretClient] | None = None,
        skip_on_error: bool = True,
    ) -> AzureAppConfig:
        """
        De-reference links from KeyVault (or even several KeyVaults) and replace the references with actual values.
        Otherwise, the values would contain simple JSON with just a secret URI instead of actual secret.

        :param client_factory: provide custom factory for SecretClient(s) if the default one
            (see default_secret_client_factory) is not working in your case.
        :param skip_on_error: if True the errors are ignored and at least the remaing portion of configuration is read;
            otherwise it will immediately fail.
        """
        self._allow_reading_keyvault_refs = True
        self._secret_client_factory = client_factory if client_factory else default_secret_client_factory
        self._skip_on_error = skip_on_error
        return self

    def get_configuration_data(self) -> dict[str, str | int | float | bool]:
        """
        Get data which should be merged into configuration.
        The keys should follow the required pattern - see documentation in developer.md.
        """
        key_filter = (
            None if self._prefix is None else f"{self._prefix}*" if not self._prefix.endswith("*") else self._prefix
        )
        # noinspection PyTypeChecker
        idx = 0 if self._prefix is None else len(self._prefix)
        result: dict[str, str | int | float | bool] = {}
        ref_keys: list[str] = []

        for kvp in self._client.list_configuration_settings(key_filter=key_filter, label_filter=self._label):
            key = kvp.key[idx:].lstrip(".") if idx > 0 else kvp.key
            key = SNAKE_CASE_REPLACE_PATTERN.sub("_", key).lower()
            value = kvp.value
            if kvp.content_type and kvp.content_type.startswith(KEYVAULT_REF_TYPE):
                ref_keys.append(key)
            result[key] = value

        if self._allow_reading_keyvault_refs and len(ref_keys) > 0:
            self._read_keyvault_refs(ref_keys, result)

        return result

    def _read_keyvault_refs(self, ref_keys: list[str], result: dict[str, str | int | float | bool]) -> None:
        cache: dict[str, SecretClient] = {}

        def fetch_secret(key: str, clients: dict[str, SecretClient]) -> tuple[str, str | None]:
            # noinspection PyBroadException
            try:
                js = json.loads(result[key])  # type: ignore[arg-type]
                kv_uri = js["uri"]
                vault_url = "/".join(kv_uri.split("/")[:3])
                secret_name = kv_uri.split("/")[-1]

                if vault_url in clients:
                    client = clients[vault_url]
                else:
                    client = self._secret_client_factory(vault_url)  # type: ignore[misc]
                    clients[vault_url] = client

                secret: KeyVaultSecret = client.get_secret(secret_name)
                return key, secret.value
            except Exception:
                if self._skip_on_error:
                    return key, None
                raise

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(fetch_secret, key, cache): key for key in ref_keys}
            for future in as_completed(futures):
                key, secret_value = future.result()
                if secret_value is not None:
                    result[key] = secret_value


def default_secret_client_factory(vault_url: str) -> SecretClient:
    """
    Create SecretClient for given vault URL using DefaultAzureCredential as credential source.
    https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python
    """
    credential = DefaultAzureCredential()
    # noinspection PyTypeChecker
    return SecretClient(vault_url=vault_url, credential=credential)
