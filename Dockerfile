# dockerfile for the Wireguard Container Endpoint
# container required cap-add=NET_ADMIN and cap-add=NET_RAW to work properly
FROM ubuntu:20.04

# Version that is displayed inside the container for the application
ARG BUILD_VERSION=undefined
ADD --chown=root:root https://raw.githubusercontent.com/WireGuard/wireguard-tools/v1.0.20210914/contrib/json/wg-json /bin/wg-json

RUN set -x \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
        curl \
        inetutils-traceroute \
        iproute2 \
        iputils-ping \
        iptables=1.8.4-3ubuntu2 \
        nano=4.8-1ubuntu1 \
        python3.8=3.8.10-0ubuntu1~20.04.4 \
        python3-pip=20.0.2-5ubuntu1.6 \
        wireguard=1.0.20200513-1~20.04.2 \
        wireguard-tools=1.0.20200513-1~20.04.2 \
	&& apt-get clean autoclean \
	&& apt-get autoremove -y \
    && chmod 755 /bin/wg-json  \
	&& rm -rf /var/lib/apt/lists/* \
    && mkdir /opt/data

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

VOLUME ["/opt/data"]

# configuration options for the container
ENV DATA_DIR="/opt/data" \
    # change the name of the endpoint within the container
    #APP_NAME="Wireguard Container Endpoint" \
    APP_ADMIN_USER="admin" \
    # a random initial password is generated if variable is unset
    #APP_ADMIN_PASSWORD="PlsChgMe" \
    APP_PORT=8000 \
    APP_HOST=0.0.0.0 \
    APP_VERSION="${BUILD_VERSION}" \
    # value in seconds that defines how often the peer status is checked
    APP_PEER_TRACKING_TIMER="10" \
    # log level
    LOG_LEVEL="info" \
    # unset UVICORN_SSL_KEYFILE to disable HTTPs
    UVICORN_SSL_KEYFILE="/opt/data/ssl/privkey.pem" \
    UVICORN_SSL_CERTFILE="/opt/data/ssl/fullchain.pem" \
    # information for the self signed certificate
    SELF_SIGNED_CERT_CN="example.com" \
    # FastAPI CORS settings
    APP_CORS_ORIGIN="*" \
    APP_CORS_METHODS="*" \
    APP_CORS_HEADERS="*" \
    # uvicorn concurrency
    WEB_CONCURRENCY=1

# the container user is root, because it uses wg-quick and various other commands to
# configure the wireguard endpoints
COPY ./webapp /opt/webapp/
COPY ./resources/runserver.bash /opt/runserver.bash

SHELL [ "/bin/bash" ]
WORKDIR /opt/webapp/

CMD ["/opt/runserver.bash"]
