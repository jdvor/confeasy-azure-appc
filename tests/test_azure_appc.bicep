param location string = resourceGroup().location
param appConfigName string = 'appc-confeasy'
param keyVaultName string = 'kv-confeasy'
param tenantId string = '4a644f9e-4a24-4895-89a9-9f159a62733b'

var label = 'dev'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    networkAcls: {
      defaultAction: 'Allow'
    }
    publicNetworkAccess: 'Enabled'
  }
}

resource kv1 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'admin-pswd-dev'
  properties: {
    value: 'admin-pswd-dev-value'
    contentType: 'text/plain'
  }
}

resource appc 'Microsoft.AppConfiguration/configurationStores@2023-03-01' = {
  name: appConfigName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
  dependsOn: [keyVault]
}

resource cfg1 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appc
  name: 'AlphaHorse'
  properties: {
    value: '1'
    contentType: 'text/plain'
  }
}

resource cfg2 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appc
  name: 'beta.gammaGoat'
  properties: {
    value: '2'
    contentType: 'text/plain'
  }
}

resource cfg3 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appc
  name: 'beta.deltaRabbit'
  properties: {
    value: '3'
    contentType: 'text/plain'
  }
}

resource cfg4 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appc
  name: 'db.connection_string$${label}'
  properties: {
    value: 'lorem ipsum dolor sit'
    contentType: 'text/plain'
  }
}

resource cfg5 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appc
  name: 'db.max_connections$${label}'
  properties: {
    value: '200'
    contentType: 'text/plain'
  }
}

resource cfg6 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appc
  name: 'kv.admin_pswd'
  properties: {
    value: '{"uri":"${keyVault.properties.vaultUri}secrets/${kv1.name}"}'
    contentType: 'application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8'
  }
}

output appcConnStr string = listKeys(appc.id, '2023-03-01').value[0].connectionString
