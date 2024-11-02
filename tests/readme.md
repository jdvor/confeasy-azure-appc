```shell
az group create --subscription {sid} --name {group} --location gremanywestcentral
az deployment group create --subscription {sid} -n deployment_1 -g {group} -f test_azure_appc.bicep
```

```shell
az group delete --subscription {sid} -n {group} --no-wait --yes
```