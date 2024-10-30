# confeasy.azure_appc

Application configuration inspired by Microsoft.Extensions.Configuration (.NET).<br/>
See details in GitHub [confeasy][confeasy_gh] ([PyPI][confeasy_pypi]).

This package is an extension to confeasy using [Azure AppConfiguration][azure] service.

## Getting started

Install required packages.

```shell
poetry add confeasy confeasy.azure_appc
# or similar command for your package manager of choice
```

In python, usually around application start:
```python

# DbOptions class is an illustrative example of strongly typed configuration.
class DbOptions:
    def __init__(self):
        self.connnection_string: str = ""
        self.max_connections: int = 100

from confeasy import Builder
from confeasy.envars import EnvironmentVariables
from confeasy.cmdline import CommandLine
from confeasy.azure_appc import AzureAppConfig

# Order of the configuration sources matters; later sources can overwrite values from earlier ones.
builder = (Builder()
           .add_source(AzureAppConfig.from_conn_str_in_envars("APPC_CONNECTION_STRING", "db.*"))
           .add_source(EnvironmentVariables("MYAPP_"))
           .add_source(CommandLine()))

config = builder.build()

# Bind configuration to a class instance and pass the instance to other objects.
options = config.bind(DbOptions(), prefix="db")

# OR pick up individual values:
db_conn_str = config.get_value("db.connection_string")
```

[azure]: https://learn.microsoft.com/en-us/azure/azure-app-configuration/overview
[confeasy_gh]: https://github.com/jdvor/confeasy
[confeasy_pypi]: https://pypi.org/project/confeasy