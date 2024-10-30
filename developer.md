# confeasy - Developer Guide

## Pre-requisites and preparing your environment

* Python 3.13.0+
* poetry 1.8.4+

Install latest poetry.<br/>
From more detailed instructions check https://python-poetry.org/docs/#installation.

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

You may need to add poetry to execution path.<br/>
Close the terminal and open it again after this command.

```powershell
[System.Environment]::SetEnvironmentVariable("Path", "$HOME\AppData\Roaming\pypoetry\venv\Scripts;$($env:Path)", "User")
```

OR update existing poetry installation

```shell
poetry self update
```

Install plugin required for command: `poetry up`.<br/>
It is an action attempting to find any possible package updates in a project.

```shell
poetry self add poetry-plugin-up
```

Change setting to create virtual environments inside the project directory under ./venv/

```shell
poetry config virtualenvs.in-project true
```

Create virtual environment for the project.
This is required only after first `git clone`.

```shell
poetry install
```

## Tasks defined in the project

(or being generally available for every poetry-based project)

```shell
poetry run poe code
```

```shell
poetry run poe test
```

```shell
poetry run poe version_and_push [ --major | --minor | --patch ] [ --tag-name-suffix "rc" ]
```

```shell
poetry run poe
```

```shell
poetry run poe type
poetry run poe citest
```

```shell
poetry install

poetry add package-name [ --group dev ]

poetry remove package-name

poetry up
```


## Publishing to PyPi

```shell
# Build the package locally. The default output directory is dist/
poetry build

# Build and publish the package to PyPI. This requires the API token.
POETRY_PYPI_TOKEN_PYPI={api-token} poetry publish --build
```