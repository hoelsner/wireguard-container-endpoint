# dockerfile for the Wireguard Container Endpoint
# container required cap-add=NET_ADMIN and cap-add=NET_RAW to work properly
FROM ubuntu:20.04

ENV PATH="/home/appuser/.local/bin:${PATH}"
ARG APP_VERSION=undefined

ADD --chown=root:root https://raw.githubusercontent.com/WireGuard/wireguard-tools/v1.0.20210914/contrib/json/wg-json /bin/wg-json

RUN set -x \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
        curl=7.68.0-1ubuntu2.7 \
        wireguard=1.0.20200513-1~20.04.2 \
        wireguard-tools=1.0.20200513-1~20.04.2 \
        iproute2=5.5.0-1ubuntu1 \
        iputils-ping=3:20190709-3 \
        inetutils-traceroute=2:1.9.4-11ubuntu0.1 \
        iptables=1.8.4-3ubuntu2 \
        nano=4.8-1ubuntu1 \
	&& apt-get clean autoclean \
	&& apt-get autoremove -y \
    && chmod 755 /bin/wg-json  \
	&& rm -rf /var/lib/apt/lists/*

# the container user is root, because it uses wg-quick and various other commands to
# configure the wireguard endpoints
USER root

CMD ["/bin/bash"]
