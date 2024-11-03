param(
    [Parameter(Mandatory=$true)][string]$SubscriptionId,
    [Parameter(Mandatory=$true)][string]$ResourceGroup
)

$appName = "confeasy_GitHub"
$scope = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup"

$appId = (az ad app create --display-name "$appName" --query appId -o tsv)

try {
    $spId = az ad sp show --id "$appId" --query id -o tsv
}
catch {}
if ([string]::IsNullOrEmpty($spId)) {
    $spId = az ad sp create --id "$appId" --query id -o tsv
}

$clientSecret = (az ad app credential reset --id "$appId" --query password -o tsv)
az role assignment create --subscription "$SubscriptionId" --assignee-object-id "$spId" --assignee-principal-type ServicePrincipal --role "App Configuration Data Reader" --scope "$scope" --only-show-errors -o none
az role assignment create --subscription "$SubscriptionId" --assignee-object-id "$spId" --assignee-principal-type ServicePrincipal --role "Key Vault Secrets User" --scope "$scope" --only-show-errors -o none
$tenantId = (az account show --query tenantId -o tsv)

Write-Host
Write-Output "AZURE_TENANT_ID: $tenantId"
Write-Output "AZURE_CLIENT_ID: $appId"
Write-Output "AZURE_CLIENT_SECRET: $clientSecret"
Write-Output "Service Principal Id: $spId"