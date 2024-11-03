#!/usr/bin/env bash

subscription_id=''
rg=''
app_name='confeasy_GitHub'

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s|--subscription) subscription_id="$2"; shift;;
        -g|--resource-group) rg="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ -z "$subscription_id" ] || [ -z "$rg" ]; then
  echo "Usage: ./app_service_principal.sh -s {SubscriptionId} -r {ResourceGroup}"
  exit 1
fi

scope="/subscriptions/$subscription_id/resourceGroups/$rg"

app_id=$(az ad app create --display-name "$app_name" --query appId -o tsv)

sp_id=$(az ad sp show --id "$app_id" --query id -o tsv 2>/dev/null)
if [ -z "$sp_id" ]; then
  sp_id=$(az ad sp create --id "$app_id" --query id -o tsv)
fi

client_secret=$(az ad app credential reset --id "$app_id" --query password -o tsv)
az role assignment create --subscription "$subscription_id" --assignee-object-id "$sp_id" --role "App Configuration Data Reader" --scope "$scope" --only-show-errors
az role assignment create --subscription "$subscription_id" --assignee-object-id "$sp_id" --role "Key Vault Secrets User" --scope "$scope" --only-show-errors

echo
echo "AZURE_TENANT_ID: $(az account show --query tenantId -o tsv)"
echo "AZURE_CLIENT_ID: $app_id"
echo "AZURE_CLIENT_SECRET: $client_secret"
echo "Service Principal Id: $sp_id"
