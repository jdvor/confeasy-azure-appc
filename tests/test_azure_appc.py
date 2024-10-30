from confeasy.azure_appc import AzureAppConfig
import pytest


@pytest.mark.integration
def test_appc():
    sut = AzureAppConfig.from_conn_str_in_envars("APPC_CONNECTION_STRING")
    actual = sut.get_configuration_data()
    assert len(actual) == 4
    assert "alpha_horse" in actual
    assert "omega_fox" in actual
    assert actual["beta.gamma_goat"] == 10