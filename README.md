# UAIssistant

## Contents

- [Requirements](#requirements)
  - [python](#install-python)
  - [poetry](#install-poetry)
  - [docker](#install-docker)
- [Install and Run](#install-and-run)
  - [Set env variables](#set-env-variables)
  - [Run locally (dev)](#run-locally-dev)
  - [Run with docker (prod)](#run-with-docker-prod)
- [Tool-functions Development](#tool-functions-development)
- [Access DB](#access-db)

## Requirements

- Python (~3.10)
- Poetry
- Docker

### Install Python

For Linux users: `sudo apt install python3.10`

For MacOS users: `brew install python@3.10`

Otherwise, please, go to the official [Python website](https://www.python.org/downloads/), download and install Python (we use `python3.10`.).

### Install Poetry

Install poetry by following instructions from the official [poetry website](https://python-poetry.org/docs/).

If you would like to build your own project with poetry, you can follow the instructions from the offical [poetry website](https://python-poetry.org/docs/basic-usage/).

### Install Docker

There are several ways to install docker:

- [Docker](https://docs.docker.com/engine/install/)
- [Rancher Desktop](https://rancherdesktop.io/) (good option for MacOS)
- [Podman](https://podman.io/)

`docker-compose` is also required. Check that you have `docker-compose` with the command `docker-compose --version`. If you don't have it, please, run the following code (for Linus and MacOS users):

```
sudo curl -L "https://github.com/docker/compose/releases/download/{VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Install and Run

First of all clone the repository:

```
git clone git@github.com:uhatikus/UAIssistant.git
cd UAIssistant
```

### Set env variables

1. Create .env file and copy the content of .env.example to .env: `cp .env.example .env`
2. Set your OPENAI_API_KEY ([get open-ai API key](https://platform.openai.com/api-keys)) and ANTHROPIC_API_KEY ([get anthropic API key](https://console.anthropic.com/settings/keys)).

### Run locally (dev)

```
# create postgres db in docker (run "make clean" if you are refreshing the db)
make db
# install poetry dependencies
make install
# start the BE
make run
```

### Run with Docker (prod)

```
# build start dockers for db and uaissistant BE application with docker-compose
docker-compose up --build
```

(you can remove `--build` if you have already built the dockere containers)

## Tool-functions Development

[Readme "How to develop tool-funtions"](uaissistant/tool_factory/README.md)

## Access DB

You can access the DB with DataGrip or DBveaver. Use the details from .env file. s

DataGrip example:
![DataGrip DB connection](readmedia/datagrip.png)
