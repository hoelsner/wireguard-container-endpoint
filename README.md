# Wireguard Container Endpoint (WGCE)

This project contains the code for a Container that provides access to a Wireguard VPN for local containers and single networks (see [scenarios.md](./docs/scenarios.md) for target Use-Cases/Scenarios).

## TODOs

* [ ] Docker based Wireguard VPN Hub/Endpoint that supports configuration via an a HTTP API (basic authentication with username and password)
* [ ] route to another Wireguard Endpoint (Hub-Topology) within the Wireguard VPN
* [ ] ability to connect to local container on the same Container Engine
* [ ] update to the peer configuration should not affect the existing tunnels (hitless configuration update)
* [ ] route to a local network outside the VPN [optional]

## How to use

TODO:

The API to configure the Wireguard Interfaces is exposed at `/api` and the swagger documentation is available at `/docs`.

## How to develop

### Setup Development Environment

Before starting, you need to install the python dependencies located at `requirements_dev.txt` optional within a `virtualenv`.

For schema management, aerich is used together with Tortoise ORM. The aerich migration environment was already initialized using the following commands:

```bash
cd webapp
aerich init --tortoise-orm utils.config.TORTOISE_ORM
aerich init-db
```

To create a new migration for the project, use the following command:

```bash
aerich migrate --name <name of migration>
```

To migrate an existing database, use the following command:

```bash
aerich upgrade
```

### Run Development Server

To start a development server, run the following command:

```bash
# use cli .py
python3 cli.py run-dev-server

# start development server directly
uvicorn app:create --factory --port=8000 --debug --host="0.0.0.0"
```

### Run Unit-Tests

To run the testcases, use the following command:

```bash
cd webapp
pytest

# or just rerun the last failed test cases
pytest --lf

# or use pytest watch
ptw
```

## How to Build and Run a Production Container

To build and start a production container, use the following commands on the repository root directory:

```bash
docker build -t localhost.local/wg-container-endpoint:dev .
docker run --rm -it \
    --cap-add=NET_ADMIN \
    --cap-add=NET_RAW \
    -p 8000:8000 \
    localhost.local/wg-container-endpoint:dev \
    /bin/bash -c "uvicorn app:create --factory --host=0.0.0.0 --port=8000"
```
