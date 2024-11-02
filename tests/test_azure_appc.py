from __future__ import annotations

from confeasy.azure_appc import KEYVAULT_REF_TYPE
from azure.appconfiguration import ConfigurationSetting
from azure.keyvault.secrets import KeyVaultSecret, SecretProperties
from confeasy.azure_appc import AzureAppConfig
from dotenv import load_dotenv
from pathlib import Path
import pytest
from typing import Any, Iterable


envfile = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=envfile)


def test_keys_are_normalized():
    mock = AzureAppConfigurationClientMock({
        "YellowHorse": "1",
        "beta.loremIpsum": "yes",
    })
    # noinspection PyTypeChecker
    sut = AzureAppConfig(mock)
    actual = sut.get_configuration_data()
    assert len(actual) == 2
    assert actual["yellow_horse"] == "1"
    assert actual["beta.lorem_ipsum"] == "yes"


# noinspection PyTypeChecker
def test_keyvault_ref_is_replaced_by_real_value():
    appc_mock = AzureAppConfigurationClientMock({
        "admin_pswd": kvref("admin_pswd"),
        "alpha": "1"
    })
    kv_mock = SecretClientMock.with_data({"admin_pswd": "pass123"})

    def cf(_: str):
        return kv_mock

    sut = AzureAppConfig(appc_mock)
    sut.allow_reading_keyvault_references(client_factory=cf, skip_on_error=False)
    actual = sut.get_configuration_data()
    assert len(actual) == 2
    assert actual["admin_pswd"] == "pass123"
    assert actual["alpha"] == "1"


# noinspection PyTypeChecker
def test_errors_are_visible_if_requested():
    appc_mock = AzureAppConfigurationClientMock({"admin_pswd": kvref("admin_pswd")})
    kv_mock = SecretClientMock.raising_error("I don't like you")

    def cf(_: str):
        return kv_mock

    sut = AzureAppConfig(appc_mock)
    sut.allow_reading_keyvault_references(client_factory=cf, skip_on_error=False)
    with pytest.raises(ValueError, match="I don't like you"):
        actual = sut.get_configuration_data()


# noinspection PyTypeChecker
def test_errors_are_swallowed_by_default():
    ref = kvref("admin_pswd")
    appc_mock = AzureAppConfigurationClientMock({
        "admin_pswd": ref,
        "alpha": "1",
    })
    kv_mock = SecretClientMock.raising_error("I don't like you")

    def cf(_: str):
        return kv_mock

    sut = AzureAppConfig(appc_mock)
    sut.allow_reading_keyvault_references(client_factory=cf)
    actual = sut.get_configuration_data()
    assert len(actual) == 2
    assert actual["admin_pswd"] == ref
    assert actual["alpha"] == "1"


@pytest.mark.integration
def test_appc_real():
    sut = AzureAppConfig.from_conn_str_in_envars("APPC_CONNECTION_STRING")
    sut.allow_reading_keyvault_references(skip_on_error=False)
    actual = sut.get_configuration_data()
    assert len(actual) >= 6
    assert "alpha_horse" in actual
    assert "beta.delta_rabbit" in actual
    assert "kv.admin_pswd" in actual
    assert actual["kv.admin_pswd"] == "admin-pswd-dev-value"


class AzureAppConfigurationClientMock:

    def __init__(self, data: dict[str, str]):
        self.data = data

    def list_configuration_settings(self, **kwargs) -> Iterable[ConfigurationSetting]:

        def ct(val: str) -> str | None:
            return KEYVAULT_REF_TYPE if ".vault.azure.net/secrets/" in val else None

        return [ConfigurationSetting(key=k, value=v, content_type=ct(v)) for k, v in self.data.items()]


class SecretClientMock:

    def __init__(self, data: dict[str, str], raises: str | None):
        self._data = data
        self._raises = raises

    def get_secret(self, name: str, version: str | None = None, **kwargs: Any) -> KeyVaultSecret:
        if self._raises:
            raise ValueError(self._raises)
        props = SecretProperties()
        return KeyVaultSecret(props, self._data[name]) if name in self._data else KeyVaultSecret(props, None)

    @classmethod
    def raising_error(cls, msg: str) -> SecretClientMock:
        return SecretClientMock({}, msg)

    @classmethod
    def with_data(cls, data: dict[str, str]) -> SecretClientMock:
        return SecretClientMock(data, None)


def kvref(name: str) -> str:
    return f'{{"uri":"https://kv-confeasy.vault.azure.net/secrets/{name}"}}'
