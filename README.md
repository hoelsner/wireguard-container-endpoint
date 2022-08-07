# WireGuard Container Endpoint (WGCE)

This Container provides a REST API to configure WireGuard interfaces and filters based on iptables on a host (for IPv4 and IPv6). The intended Use-Cases/Scenarios are described [here](./docs/scenarios.md).

## How to use

First, you need to start the container with the following command:

```
docker run -d \
    --name=wgce \
    --cap-add=NET_ADMIN \
    -p 8000:8000 \
    --volume wgce_data:/opt/data \
    --sysctl net.ipv4.ip_forward=1 \
    --sysctl net.ipv4.conf.all.src_valid_mark=1 \
    --sysctl net.ipv6.conf.all.forwarding=1 \
    --sysctl net.ipv6.conf.all.disable_ipv6=0 \
    docker.io/hoelsner/wireguard-container-endpoint:latest
```

The sysctl settings are required to support routing and IPv6 within the Container. By default, a new instance will use a `admin` user together with a random password that is stored at `/opt/data/.generated_password` (retrieve with `docker exec -it wgce /bin/bash -c "cat /opt/data/.generated_password"`). You can also specify the admin password as `APP_ADMIN_PASSWORD` environment variable, if you want to use a predefined value.

The API to configure the WireGuard Interfaces and filters is exposed by default at `https://127.0.0.1:8000/api` and the OpenAPI/Swagger documentation is available at `https://127.0.0.1:8000/docs`.

### Application Configuration

Usually, you can start the container without any additional configuration. By default, all data that must be persistet is stored in the Container at `/opt/data`. This directory is defined as a volume by default.

The REST API will be availalbe on port `8000` using a self signed certificate. To replace the HTTPs certificate, replace the files at `/opt/data/ssl` or set the `UVICORN_SSL_KEYFILE` and `UVICORN_SSL_CERTFILE` environment variable to a different file. The log messages of the container are only printed to stdout.

The following table describes the configuration values for the container.

| Name                      | Description                                                                                                                                                                                                                      | default value                 | example value                 |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|-------------------------------|
| `APP_NAME`                | Name of the endpoint which is used as the application name on the API                                                                                                                                                            | ---                           | *unset*                       |
| `APP_ADMIN_USER`          | Username for admin access to the API                                                                                                                                                                                             | `admin`                       | `admin`                       |
| `APP_ADMIN_PASSWORD`      | Password for the admin access on the API - if not set, a admin password is generated as part of the Container start                                                                                                              | *unset*                       | `PlsChgMe`                    |
| `APP_PORT`                | port where the HTTP API is accessbile                                                                                                                                                                                            | `8000`                        | `8000`                        |
| `APP_HOST`                | Host IP where the application should be bound to *(should not be changed)*                                                                                                                                                       | `0.0.0.0`                     | `0.0.0.0`                     |
| `APP_PEER_TRACKING_TIMER` | value in seconds that defines how often the peer status is checked. If there is no key exchange for 2 minutes, a peer is considered as dead and the host route is removed from the local routing table. (change not recommended) | `10`                          | `10`                          |
| `LOG_LEVEL`               | logging level for the container                                                                                                                                                                                                  | `info`                        | `info`                        |
| `UVICORN_SSL_KEYFILE`     | path to keyfile for HTTPs within the Container                                                                                                                                                                                   | `/opt/data/ssl/privkey.pem`   | `/opt/data/ssl/privkey.pem`   |
| `UVICORN_SSL_CERTFILE`    | path to certfile for HTTPs within the Container                                                                                                                                                                                  | `/opt/data/ssl/fullchain.pem` | `/opt/data/ssl/fullchain.pem` |
| `SELF_SIGNED_CERT_CN`     | CN value if a self-signed certificate is created                                                                                                                                                                                 | `example.com`                 | `example.com`                 |
| `APP_CORS_ORIGIN`         | CORS origin setting for FastAPI                                                                                                                                                                                                  | ---                           | `*`                           |
| `APP_CORS_METHODS`        | CORS methods setting for FastAPI                                                                                                                                                                                                 | ---                           | `*`                           |
| `APP_CORS_HEADERS`        | CORS headers setting for FastAPI                                                                                                                                                                                                 | ---                           | `*`                           |
| `DISABLE_HTTPS`           | set this environment variable to any value will disable HTTPs on the admin interface (not recommended)                                                                                                                           | ---                           | *unset*                       |
| `DEBUG`                   | enables the debug mode for the application (only for development)                                                                                                                                                                | `False`                       | `False`                       |
| `WG_CONFIG_DIR`           | location, where the WireGuard configuration files should be stored *(should not be changed)*                                                                                                                                     | `/etc/wireguard`              | `/etc/wireguard`              |
| `DATA_DIR`                | data directory where all information from the container are stored *(should not be changed)*                                                                                                                                    | ---                           | `/opt/data`                   |

### Initial Configuration

The following environment variables are required to configure the Container at the first boot with an Wireguard interface and peer:

| Name                             | Description                                                                                                            | default value | example value                                  |
|----------------------------------|------------------------------------------------------------------------------------------------------------------------|---------------|------------------------------------------------|
| `INIT_INTF_NAME`                 | initial WireGuard Interface                                                                                            | ---           | `wg16`                                         |
| `INIT_INTF_LISTEN_PORT`          | port for the interface                                                                                                 | `51820`       | `51820`                                        |
| `INIT_INTF_PRIVATE_KEY`          | private key for the interface                                                                                          | ---           | `gGIwjTnOwUw7tTnNciJDHk5m8+BVUYNMrsx5TFkXVUA=` |
| `INIT_INTF_CIDR_ADDRESSES`       | IPv4/IPv6 addresses on the interface                                                                                   | ---           | `10.1.1.1/32, FD00:1::1/128`                   |
| `INIT_POLICY_NAME`               | policy name for the interface                                                                                          | `base policy` | `base policy`                                  |
| `INIT_POLICY_NAT_ENABLE`         | enable IPv4/IPv6 NAT                                                                                                   | `False`       | `False`                                        |
| `INIT_POLICY_ALLOW_ADMIN`        | allow access to WireGuard Admin Interface thought the WireGuard interface                                              | `True`        | `True`                                         |
| `INIT_PEER_PUBLIC_KEY`           | public key of the first peer                                                                                           | ---           | `gGIwjTnOwUw7tTnNciJDHk5m8+BVUYNMrsx5TFkXVUA=` |
| `INIT_PEER_PERSISTENT_KEEPALIVE` | WireGuard keepalive for peers                                                                                          | `30`          | `60`                                           |
| `INIT_PEER_ENDPOINT`             | target host for the peer connection                                                                                    | ---           | `example.host.com:51820`                       |
| `INIT_PEER_CIDR_ROUTES`          | routes/remote targets that are reachable via the peer                                                                  | ---           | `10.1.1.1/32, FD00:1::1/128`                   |

Furthermore, the following options may be required if NAT or a PSK should be used:

| Name                             | Description                                                                                                            | default value | example value                                  |
|----------------------------------|------------------------------------------------------------------------------------------------------------------------|---------------|------------------------------------------------|
| `INIT_POLICY_NAT_INTF`           | (optional) interface name for the NAT rules (requires `INIT_POLICY_NAT_ENABLE` to `True`), required to get NAT working | ---           | `eth0`                                         |
| `INIT_PEER_PRE_SHARED_KEY`       | (optional) pre shared key for the peer                                                                                 | `None`        | `INIT_PEER_PRE_SHARED_KEY`                     |

## How to develop

### Setup Development Environment

Before starting, you need to install python 3.8 on a linux or macos machine together with the dependencies located at `requirements_dev.txt` (optionally within a `virtualenv`).

Parts of the application depends on the following packages that must be installed:

```bash
sudo apt-get install -y wireguard wireguard-tools
```

The repository also contains a vscode development Container, which was primarily used during the development. See https://code.visualstudio.com/docs/remote/containers for additional information.

### Database and Schema Migration

The configuration database is stored in a sqlite database within the application. For schema management, aerich is used together with Tortoise ORM.

The aerich migration environment was already initialized with the following command:

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

This command is automatically run, if an instance is started as part of the `resources/runserver.bash` script. The output is stored at `/opt/data/aerich.log`.

### Run Development Server

To start a development server, run the following command:

```bash
# use cli .py
python3 cli.py run-dev-server

# start development server directly using uvicorn
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

How to run the end-to-end tests is described at [test/README.md](tests/README.md). Within the end-to-end tests, a NGINX test container is created that exposes IPv4 and IPv6 endpoints based on `nginxdemos/nginx-hello`. The Dockerfile for this "test-service" is available at `resources/nginx-hello-ipv6`.

### Build and Run the Container locally

To build and start a production container, use the following commands on the repository root directory:

```bash
docker build --pull -t localhost.local/wg-container-endpoint:dev .
docker run -d -it \
    --name=wgce_dev \
    --cap-add=NET_ADMIN \
    --cap-add=NET_RAW \
    -p 8000:8000 \
    --volume wgce_data_dev:/opt/data \
    --sysctl net.ipv4.ip_forward=1 \
    --sysctl net.ipv4.conf.all.src_valid_mark=1 \
    --sysctl net.ipv6.conf.all.forwarding=1 \
    --sysctl net.ipv6.conf.all.disable_ipv6=0 \
    localhost.local/wg-container-endpoint:dev
```
