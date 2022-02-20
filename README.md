# Wireguard Container Endpoint (WGCE)

The Container provides a REST API to configure Wireguard interfaces and iptable filter on a host. The intended Use-Cases/Scenarios are described [here](./docs/scenarios.md).

## TO-DO

* [ ] Docker based Wireguard VPN Hub/Endpoint that supports configuration via an a HTTP API (basic authentication with username and password)
* [ ] route to another Wireguard Endpoint (Hub-Topology) within the Wireguard VPN
* [ ] ability to connect to local container on the same Container Engine
* [ ] update to the peer configuration should not affect the existing tunnels (hitless configuration update)
* [ ] route to a local network outside the VPN [optional]

## How to use

TODO: add how to use section

The API to configure the Wireguard Interfaces is exposed at `/api` and the swagger documentation is available at `/docs`.

## How to Build and Run the Container

To build and start a production container, use the following commands on the repository root directory:

```bash
docker build -t localhost.local/wg-container-endpoint:dev .
docker run --rm -it \
    --cap-add=NET_ADMIN \
    --cap-add=NET_RAW \
    -p 443:8000 \
    localhost.local/wg-container-endpoint:dev
```

## How to develop

### Setup Development Environment

Before starting, you need to install the python dependencies located at `requirements_dev.txt` optional within a `virtualenv`.

### Database and Schema Migration

For schema management, aerich is used together with Tortoise ORM. The aerich migration environment is already initialized with the following command:

```bash
cd webapp
aerich init --tortoise-orm utils.config.TORTOISE_ORM
aerich init-db
```

To create a new migration for the application, use the following command:

```bash
aerich migrate --name <name of migration>
```

To migrate an existing database, use the following command:

```bash
aerich upgrade
```

This command is automatically run, if an instance of the Application is started as part of the `resources/runserver.bash` script.

### Run Development Server

To start a development server, run the following command:

```bash
# use cli .py
python3 cli.py run-dev-server

# start development server directly
uvicorn app.fast_api:create --factory --port=8000 --debug --host="0.0.0.0"
```

### Run Unit-Tests

To run the unit-testcases, use the following command:

```bash
cd webapp
pytest

# or just rerun the last failed test cases
pytest --lf
```

## Run E2E tests

To test End-to-End reachability, a NGINX test container that exposes IPv4 and IPv6 endpoints based on `nginxdemos/nginx-hello` is used and stored at `resources/nginx-hello-ipv6`.
