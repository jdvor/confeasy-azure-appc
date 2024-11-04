# Preparing Infrastructure for Integration Tests

Tests marked with `@pytest.mark.integration` require actual Azure resources, specifically App Configuration and Key Vault.

Requirements:
1) Create a new Azure resource group.
2) Provision App Configuration and Key Vault resources.
3) Configure specific keys and values in App Configuration and Key Vault as required for the tests.
4) Create a managed identity and service principal to allow the tests to run successfully outside the context of an authenticated user on a local machine.
5) Retrieve the necessary authentication details and set them as environment variables, enabling DefaultAzureCredential to access them.

#### Requirement 1-3:

```shell
az login
./infra.sh -t "{tenant_id}" -s "{subscription_id}" [ -g "{resource_group}" ]
```

#### Requirement 4:

```shell
az login
./app_service_principal.sh -s "{subscription_id}" -g "{resource_group}"
```

#### Requirement 5:

The output of `app_service_principal.sh` contains necessary authentication details you can use to create GitHub secrets, local .env file, etc.

* `AZURE_CLIENT_ID`
* `AZURE_CLIENT_SECRET`
* `AZURE_TENANT_ID`