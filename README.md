# Wireguard Container Endpoint (WGCE)

This project contains the code for a Container that provides access to a Wireguard VPN for local containers and single networks (see [scenarios.md](./docs/scenarios.md) for target Use-Cases/Scenarios).

## TODO

* [ ] Docker based Wireguard VPN Hub/Endpoint that supports configuration via an a HTTP API (basic authentication with username and password)
* [ ] route to another Wireguard Endpoint (Hub-Topology) within the Wireguard VPN
* [ ] ability to connect to local container on the same Container Engine
* [ ] update to the peer configuration should not affect the existing tunnels (hitless configuration update)
* [ ] route to a local network outside the VPN [optional]

## How to Build

```
docker build -t localhost.local/wg-container-endpoint:dev .
docker run --rm -it \
    --cap-add=NET_ADMIN \
    --cap-add=NET_RAW \
    localhost.local/wg-container-endpoint:dev
```