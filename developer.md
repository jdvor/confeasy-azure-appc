# Dataverse Python Jobs

Guides for developers:

* [Preparing infrastructure for the jobs](infra/readme.md)
* [How to dockerize the jobs](jobs/readme.md)
* [How to deploy the jobs](deploy/readme.md)

## Operations

TBD: how to have visibility to what the jobs are doing in cloud environment when executed.


poetry self update


poetry config --list
poetry config virtualenvs.in-project true
poetry config --unset virtualenvs.in-project

poetry self add poetry-plugin-up


export PATH="$HOME/dev/terra/python-ci:$PATH"

[System.Environment]::SetEnvironmentVariable("Path", "$HOME\dev\terra\python-ci;$($env:Path)", "User")



poetry install
poetry up



poetry run poe --help