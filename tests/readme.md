```shell
az group create --subscription {sid} --name {group} --location gremanywestcentral
az deployment group create --subscription {sid} -n deployment_1 -g {group} -f test_azure_appc.bicep

az group delete --subscription {sid} -n {group} --no-wait --yes
```


az deployment group create --subscription 0cf44585-c346-4ff2-896f-c170c3cd169e -n deployment_1 -g jd-temp -f test_azure_appc.bicep