import os
import shutil
import time
import requests
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass, field

import docker


@dataclass
class ScenarioOneData:
    """configuration data for the test cases
    """
    image_name: str = "localhost.local/wg-container-endpoint"
    image_tag: str = "4testing"
    tmp_dir_base: str = "./tmp"
    hub_api_endpoint: str = "https://localhost:8000"
    client_1_api_endpoint: str = "https://localhost:8001"
    hub_admin_endpoint: str = "https://172.29.1.1:8000"
    client_1_admin_endpoint: str = "https://172.29.1.16:8001"

    http_ping_ipv4_endpoint: str = "172.29.0.3"
    alt_http_ping_ipv6_endpoint: str = "FD00::0:3"
    hub_ping_endpoints: list = field(default_factory=lambda: [
        "172.29.1.1",
        # network gatways on hub site
        "172.29.0.1"
    ])
    http_ipv4_endpoint: str = "http://172.29.0.3:8080"
    http_ipv6_endpoint: str = "http://[FD00::0:3]:8080"
    alt_http_ipv4_endpoint: str = "http://172.29.0.3:8888"
    alt_http_ipv6_endpoint: str = "http://[FD00::0:3]:8888"


@dataclass
class ScenarioTwoData:
    """configuration data for the test cases
    """
    image_name: str = "localhost.local/wg-container-endpoint"
    image_tag: str = "4testing"
    tmp_dir_base: str = "./tmp"
    hub_api_endpoint: str = "https://localhost:8000"
    client_1_api_endpoint: str = "https://localhost:8001"
    temp_hub_api_endpoint: str = "https://localhost:8002"
    client_2_api_endpoint: str = "https://localhost:8003"

    http_ping_ipv4_endpoint: str = "172.29.0.3"
    alt_http_ping_ipv6_endpoint: str = "FD00::0:3"
    hub_ping_endpoints: list = field(default_factory=lambda: [
        "172.29.1.1",
        # network gatways on hub site
        "172.29.0.1"
    ])
    http_ipv4_endpoint: str = "http://172.29.0.3:8080"
    http_ipv6_endpoint: str = "http://[FD00::0:3]:8080"
    alt_http_ipv4_endpoint: str = "http://172.29.0.3:8888"
    alt_http_ipv6_endpoint: str = "http://[FD00::0:3]:8888"
    temp_http_ipv4_endpoint: str = "http://172.29.0.19:8080"
    temp_http_ipv6_endpoint: str = "http://[FD00::1:3]:8080"
    temp_alt_http_ipv4_endpoint: str = "http://172.29.0.19:8888"
    temp_alt_http_ipv6_endpoint: str = "http://[FD00::1:3]:8888"


def create_scenario_1():
    """create containers and networks for scenario 1
    """
    scenario_data = ScenarioOneData()
    client = docker.from_env()

    os.makedirs(scenario_data.tmp_dir_base, exist_ok=True)
    os.makedirs(os.path.join(scenario_data.tmp_dir_base, "wg_hub"), exist_ok=True)
    os.makedirs(os.path.join(scenario_data.tmp_dir_base, "wg_client_1"), exist_ok=True)

    # build images
    client.images.build(
        path=os.path.join(".."),
        tag=f"{scenario_data.image_name}:{scenario_data.image_tag}",
        pull=True,
        rm=True
    )
    client.images.build(
        path=os.path.join("..", "resources", "nginx-hello-ipv6"),
        dockerfile="Dockerfile-plain-text",
        tag="localhost.local/nginx-hello-ipv6:latest",
        pull=True,
        rm=True
    )

    # create serivces network
    wg_transit_network = client.networks.create(
        name="wg_transit",
        enable_ipv6=True,
        options={
            "com.docker.network.enable_ipv6": "true"
        },
        ipam=docker.types.IPAMConfig(
            driver="default",
            pool_configs=[
                docker.types.IPAMPool(
                    subnet="172.29.0.0/28",
                    gateway="172.29.0.1"
                ),
                docker.types.IPAMPool(
                    subnet="FD00::0:0/112",
                    gateway="FD00::0:1"
                )
            ]
        )
    )
    wg_public_network = client.networks.create(name="wg_public")

    # create hub container
    wg_hub_container = client.containers.create(
        image=f"{scenario_data.image_name}:{scenario_data.image_tag}",
        detach=True,
        ports={
            "8000/tcp": ("0.0.0.0", 8000),
            "51820/udp": ("0.0.0.0", 51820)
        },
        cap_add=["NET_ADMIN", "NET_RAW"],
        environment={
            "DEBUG": "False",
            "APP_NAME": "WG Hub",
            "APP_PORT": "8000",
            "APP_VERSION": "scenario-1-test",
            "APP_ADMIN_USER": "wg_hub",
            "APP_ADMIN_PASSWORD": "wg_hub",
            "LOG_LEVEL": "info",
            # initial configuration
            "INIT_INTF_NAME": "wg16",
            "INIT_INTF_LISTEN_PORT": "51820",
            "INIT_INTF_PRIVATE_KEY": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
            "INIT_INTF_CIDR_ADDRESSES": "172.29.1.1/32, FD00:1::1/128",
            "INIT_POLICY_NAT_ENABLE": "True",
            "INIT_POLICY_NAT_INTF": "eth0",
            "INIT_POLICY_ALLOW_ADMIN": "False",
            "INIT_PEER_PUBLIC_KEY": "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=",
            "INIT_PEER_PRE_SHARED_KEY": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
            "INIT_PEER_PERSISTENT_KEEPALIVE": "5",
            "INIT_PEER_ENDPOINT": "wg_client_1:51821",
            "INIT_PEER_CIDR_ROUTES": "172.29.1.16/32, FD00:1::16/128",
        },
        volumes=[f'{os.path.abspath(os.path.join(scenario_data.tmp_dir_base, "wg_hub"))}:/opt/data'],
        sysctls={
            "net.ipv4.ip_forward": "1",
            "net.ipv4.conf.all.src_valid_mark": "1",
            "net.ipv6.conf.all.forwarding": "1",
            "net.ipv6.conf.all.disable_ipv6": "0",
        },
        name="wg_hub"
    )
    wg_transit_network.connect(wg_hub_container, ipv4_address="172.29.0.2", ipv6_address="FD00::0:2")
    wg_public_network.connect(wg_hub_container)
    wg_hub_container.start()

    # create web-server service
    nginx_demo_container = client.containers.create(
        image="localhost.local/nginx-hello-ipv6:latest",
        detach=True,
        network="wg_transit",
        name="nginx_demo",
        sysctls={
            "net.ipv6.conf.all.disable_ipv6": "0",
        }
    )
    wg_transit_network.connect(nginx_demo_container, ipv4_address="172.29.0.3", ipv6_address="FD00::0:3")
    nginx_demo_container.start()

    # create spoke container
    wg_client_1_container = client.containers.create(
        image=f"{scenario_data.image_name}:{scenario_data.image_tag}",
        detach=True,
        ports={
            "8001/tcp": ("0.0.0.0", 8001)
        },
        cap_add=["NET_ADMIN", "NET_RAW"],
        environment={
            "DEBUG": "False",
            "APP_NAME": "WG Client 1",
            "APP_PORT": "8001",
            "APP_VERSION": "scenario-1-test",
            "APP_ADMIN_USER": "wg_spoke",
            "APP_ADMIN_PASSWORD": "wg_spoke",
            "LOG_LEVEL": "info",
            # initial configuration
            "INIT_INTF_NAME": "wg15",
            "INIT_INTF_LISTEN_PORT": "51821",
            "INIT_INTF_PRIVATE_KEY": "sJVz9zldsUb48AtGULMRPTNTF0UfX+XF2AHKtopYLlU=",
            "INIT_INTF_CIDR_ADDRESSES": "172.29.1.16/32, fd00:1::16/128",
            "INIT_POLICY_NAT_ENABLE": "False",
            "INIT_POLICY_ALLOW_ADMIN": "True",
            "INIT_PEER_PUBLIC_KEY": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
            "INIT_PEER_PRE_SHARED_KEY": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
            "INIT_PEER_PERSISTENT_KEEPALIVE": "5",
            "INIT_PEER_ENDPOINT": "wg_hub:51820",
            "INIT_PEER_CIDR_ROUTES": "172.29.0.0/24, 172.29.1.0/24, fd00::/64, fd00:1::/64",
        },
        volumes=[f'{os.path.abspath(os.path.join(scenario_data.tmp_dir_base, "wg_client_1"))}:/opt/data'],
        sysctls={
            "net.ipv4.ip_forward": "1",
            "net.ipv4.conf.all.src_valid_mark": "1",
            "net.ipv6.conf.all.forwarding": "1",
            "net.ipv6.conf.all.disable_ipv6": "0",
        },
        name="wg_client_1"
    )
    wg_public_network.connect(wg_client_1_container)
    wg_client_1_container.start()


def destroy_scenario_1():
    """destroy scenario 1 container and networks
    """
    scenario_data = ScenarioOneData()
    client = docker.from_env()

    client.containers.list(filters={"name": "nginx_demo"})[0].remove(force=True)
    client.containers.list(filters={"name": "wg_client_1"})[0].remove(force=True)
    client.containers.list(filters={"name": "wg_hub"})[0].remove(force=True)
    client.networks.list(names="wg_transit")[0].remove()
    client.networks.list(names="wg_public")[0].remove()
    shutil.rmtree(scenario_data.tmp_dir_base)


def create_scenario_2():
    """create containers and networks for scenario 2
    """
    scenario_data = ScenarioTwoData()
    client = docker.from_env()

    os.makedirs(scenario_data.tmp_dir_base, exist_ok=True)
    os.makedirs(os.path.join(scenario_data.tmp_dir_base, "wg_hub"), exist_ok=True)
    os.makedirs(os.path.join(scenario_data.tmp_dir_base, "wg_client_1"), exist_ok=True)
    os.makedirs(os.path.join(scenario_data.tmp_dir_base, "wg_temp_hub"), exist_ok=True)
    os.makedirs(os.path.join(scenario_data.tmp_dir_base, "wg_client_2"), exist_ok=True)

    # build images
    client.images.build(
        path=os.path.join(".."),
        tag=f"{scenario_data.image_name}:{scenario_data.image_tag}",
        pull=True,
        rm=True
    )
    client.images.build(
        path=os.path.join("..", "resources", "nginx-hello-ipv6"),
        dockerfile="Dockerfile-plain-text",
        tag="localhost.local/nginx-hello-ipv6:latest",
        pull=True,
        rm=True
    )

    # create serivces network
    wg_transit_network = client.networks.create(
        name="wg_transit",
        enable_ipv6=True,
        options={
            "com.docker.network.enable_ipv6": "true"
        },
        ipam=docker.types.IPAMConfig(
            driver="default",
            pool_configs=[
                docker.types.IPAMPool(
                    subnet="172.29.0.0/28",
                    gateway="172.29.0.1"
                ),
                docker.types.IPAMPool(
                    subnet="FD00::0:0/112",
                    gateway="FD00::0:1"
                )
            ]
        )
    )
    wg_transit_temp_network = client.networks.create(
        name="wg_transit_temp",
        enable_ipv6=True,
        options={
            "com.docker.network.enable_ipv6": "true"
        },
        ipam=docker.types.IPAMConfig(
            driver="default",
            pool_configs=[
                docker.types.IPAMPool(
                    subnet="172.29.0.16/28",
                    gateway="172.29.0.17"
                ),
                docker.types.IPAMPool(
                    subnet="FD00::1:0/112",
                    gateway="FD00::1:1"
                )
            ]
        )
    )
    # for the mesh between the hubs
    wg_public_transit_network = client.networks.create(name="wg_public_transit")
    # for client connectivity to the hubs
    wg_public_network = client.networks.create(name="wg_public")

    # create hub container
    wg_hub_container = client.containers.create(
        image=f"{scenario_data.image_name}:{scenario_data.image_tag}",
        detach=True,
        ports={
            "8000/tcp": ("0.0.0.0", 8000),
            "51820/udp": ("0.0.0.0", 51820),
            "51821/udp": ("0.0.0.0", 51821)
        },
        cap_add=["NET_ADMIN", "NET_RAW"],
        environment={
            "DEBUG": "False",
            "APP_NAME": "WG Perm Hub",
            "APP_PORT": "8000",
            "APP_VERSION": "scenario-2-test",
            "APP_ADMIN_USER": "wg_hub",
            "APP_ADMIN_PASSWORD": "wg_hub",
            "LOG_LEVEL": "info",
            # initial configuration
            "INIT_INTF_NAME": "wg16",
            "INIT_INTF_LISTEN_PORT": "51820",
            "INIT_INTF_PRIVATE_KEY": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
            "INIT_INTF_CIDR_ADDRESSES": "172.29.1.1/32, FD00:1::1/128",
            "INIT_POLICY_NAT_ENABLE": "True",
            "INIT_POLICY_NAT_INTF": "eth0",
            "INIT_POLICY_ALLOW_ADMIN": "False",
            "INIT_PEER_PUBLIC_KEY": "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=",
            "INIT_PEER_PRE_SHARED_KEY": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
            "INIT_PEER_PERSISTENT_KEEPALIVE": "5",
            "INIT_PEER_ENDPOINT": "wg_client_1:51821",
            "INIT_PEER_CIDR_ROUTES": "172.29.1.16/32, FD00:1::16/128",
        },
        volumes=[f'{os.path.abspath(os.path.join(scenario_data.tmp_dir_base, "wg_hub"))}:/opt/data'],
        sysctls={
            "net.ipv4.ip_forward": "1",
            "net.ipv4.conf.all.src_valid_mark": "1",
            "net.ipv6.conf.all.forwarding": "1",
            "net.ipv6.conf.all.disable_ipv6": "0",
        },
        name="wg_hub"
    )
    wg_transit_network.connect(wg_hub_container, ipv4_address="172.29.0.2", ipv6_address="FD00::0:2")
    wg_public_network.connect(wg_hub_container)
    wg_public_transit_network.connect(wg_hub_container)
    wg_hub_container.start()

    # create web-server service on permanent hub
    nginx_demo_container = client.containers.create(
        image="localhost.local/nginx-hello-ipv6:latest",
        detach=True,
        network="wg_transit",
        name="nginx_demo",
        sysctls={
            "net.ipv6.conf.all.disable_ipv6": "0",
        }
    )
    wg_transit_network.connect(nginx_demo_container, ipv4_address="172.29.0.3", ipv6_address="FD00::0:3")
    nginx_demo_container.start()

    # create temp hub container
    wg_temp_hub_container = client.containers.create(
        image=f"{scenario_data.image_name}:{scenario_data.image_tag}",
        detach=True,
        ports={
            "8002/tcp": ("0.0.0.0", 8002),
            "51822/udp": ("0.0.0.0", 51822),
            "51819/udp": ("0.0.0.0", 51819)
        },
        cap_add=["NET_ADMIN", "NET_RAW"],
        environment={
            "DEBUG": "False",
            "APP_NAME": "WG Temp Hub",
            "APP_PORT": "8002",
            "APP_VERSION": "scenario-2-test",
            "APP_ADMIN_USER": "wg_temp_hub",
            "APP_ADMIN_PASSWORD": "wg_temp_hub",
            "LOG_LEVEL": "info",
            # initial configuration
            "INIT_INTF_NAME": "wg13",
            "INIT_INTF_LISTEN_PORT": "51822",
            "INIT_INTF_PRIVATE_KEY": "iFcS9ZxSyCzXP5mRPTSJK61Ble7WK52Cg7x3ZJ6zj2I=",
            "INIT_INTF_CIDR_ADDRESSES": "172.29.0.242/32, FD00::FFFF:242/128",
            "INIT_POLICY_NAT_ENABLE": "True",
            "INIT_POLICY_NAT_INTF": "eth0",
            "INIT_POLICY_ALLOW_ADMIN": "True",
            "INIT_PEER_PUBLIC_KEY": "h65D5oJpkgS8NQmyBWo2knXb1bHDgw5KCJ72HxczYlY=",
            "INIT_PEER_PRE_SHARED_KEY": "VAh4Pvn05h9BM4wniYGr00FQYu7Lq8tCgh8YpxpaC8Y=",
            "INIT_PEER_PERSISTENT_KEEPALIVE": "5",
            "INIT_PEER_ENDPOINT": "wg_hub:51821",
            "INIT_PEER_CIDR_ROUTES": "172.29.0.240/28, FD00::FFFF:0/112, 172.29.0.0/24, FD00::/64, 172.29.1.0/24, FD00:1::/64",
        },
        volumes=[f'{os.path.abspath(os.path.join(scenario_data.tmp_dir_base, "wg_temp_hub"))}:/opt/data'],
        sysctls={
            "net.ipv4.ip_forward": "1",
            "net.ipv4.conf.all.src_valid_mark": "1",
            "net.ipv6.conf.all.forwarding": "1",
            "net.ipv6.conf.all.disable_ipv6": "0",
        },
        name="wg_temp_hub"
    )
    wg_transit_temp_network.connect(wg_temp_hub_container, ipv4_address="172.29.0.18", ipv6_address="FD00::1:2")
    wg_public_network.connect(wg_temp_hub_container)
    wg_public_transit_network.connect(wg_temp_hub_container)
    wg_temp_hub_container.start()

    # create web-server service on temp hub
    nginx_temp_demo_container = client.containers.create(
        image="localhost.local/nginx-hello-ipv6:latest",
        detach=True,
        network="wg_transit_temp",
        name="nginx_demo_temp",
        sysctls={
            "net.ipv6.conf.all.disable_ipv6": "0",
        }
    )
    wg_transit_temp_network.connect(nginx_temp_demo_container, ipv4_address="172.29.0.19", ipv6_address="FD00::1:3")
    nginx_temp_demo_container.start()

    # create client 1 container
    wg_client_1_container = client.containers.create(
        image=f"{scenario_data.image_name}:{scenario_data.image_tag}",
        detach=True,
        ports={
            "8001/tcp": ("0.0.0.0", 8001)
        },
        cap_add=["NET_ADMIN", "NET_RAW"],
        environment={
            "DEBUG": "False",
            "APP_NAME": "WG Client 1",
            "APP_PORT": "8001",
            "APP_VERSION": "scenario-1-test",
            "APP_ADMIN_USER": "wg_spoke",
            "APP_ADMIN_PASSWORD": "wg_spoke",
            "LOG_LEVEL": "info",
            # initial configuration
            "INIT_INTF_NAME": "wg1",
            "INIT_INTF_LISTEN_PORT": "51818",
            "INIT_INTF_PRIVATE_KEY": "sJVz9zldsUb48AtGULMRPTNTF0UfX+XF2AHKtopYLlU=",
            "INIT_INTF_CIDR_ADDRESSES": "172.29.1.16/32, fd00:1::16/128",
            "INIT_POLICY_NAT_ENABLE": "False",
            "INIT_POLICY_ALLOW_ADMIN": "True",
            "INIT_PEER_PUBLIC_KEY": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
            "INIT_PEER_PRE_SHARED_KEY": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
            "INIT_PEER_PERSISTENT_KEEPALIVE": "5",
            "INIT_PEER_ENDPOINT": "wg_hub:51820",
            "INIT_PEER_CIDR_ROUTES": "172.29.0.0/24, 172.29.1.0/24, fd00::/64, fd00:1::/64",
        },
        volumes=[f'{os.path.abspath(os.path.join(scenario_data.tmp_dir_base, "wg_client_1"))}:/opt/data'],
        sysctls={
            "net.ipv4.ip_forward": "1",
            "net.ipv4.conf.all.src_valid_mark": "1",
            "net.ipv6.conf.all.forwarding": "1",
            "net.ipv6.conf.all.disable_ipv6": "0",
        },
        name="wg_client_1"
    )
    wg_public_network.connect(wg_client_1_container)
    wg_client_1_container.start()

    # wait for some seconds to get all up and running, then configure the rest of the tunnels
    time.sleep(30)

    # create VPN interconnect on Permanent hub
    wg15_interface = requests.post(f"{scenario_data.hub_api_endpoint}/api/wg/interfaces", json={
        "intf_name": "wg15",
        "description": "VPN interconnect",
        "listen_port": 51821,
        "private_key": "kGv97FqVfHYCioosfTkoWafuWVjwELRziKctegtK6mk=",
        "table": "auto",
        "cidr_addresses": "172.29.0.241/32, FD00::FFFF:241/128",
    }, verify=False, auth=HTTPBasicAuth("wg_hub", "wg_hub")).json()
    requests.post(f"{scenario_data.hub_api_endpoint}/api/wg/interface/peers", json={
        "public_key": "xY8j0XvlDH80/2XW40SVtdp6yIXBcqhDtu1YHmE3jHI=",
        "friendly_name": "Hub interconnect",
        "description": "",
        "persistent_keepalives": 5,
        "preshared_key": "VAh4Pvn05h9BM4wniYGr00FQYu7Lq8tCgh8YpxpaC8Y=",
        "endpoint": "wg_temp_hub:51822",
        "cidr_routes": "172.29.0.242/32, FD00::FFFF:242/128, 172.29.0.16/28, FD00::1:0/112",
        "wg_interface_id": wg15_interface["instance_id"]
    }, verify=False, auth=HTTPBasicAuth("wg_hub", "wg_hub"))

    # create wg14 on temporary hub
    wg14_interface = requests.post(f"{scenario_data.temp_hub_api_endpoint}/api/wg/interfaces", json={
        "intf_name": "wg14",
        "description": "client connect",
        "listen_port": 51819,
        "private_key": "eDXKtwt2kQ5snGee+TpYc4rK5wnYv+W+4Hi4kRJZm1U=",
        "table": "auto",
        "cidr_addresses": "172.29.1.2/32, FD00:1::2/128",
    }, verify=False, auth=HTTPBasicAuth("wg_temp_hub", "wg_temp_hub")).json()

    # create client entry on temporary hub
    requests.post(f"{scenario_data.temp_hub_api_endpoint}/api/wg/interface/peers", json={
        "public_key": "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=",
        "friendly_name": "client 1",
        "description": "",
        "persistent_keepalives": 5,
        "preshared_key": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
        "endpoint": "",
        "cidr_routes": "172.29.1.16/32, FD00:1::16/128",
        "wg_interface_id": wg14_interface["instance_id"]
    }, verify=False, auth=HTTPBasicAuth("wg_temp_hub", "wg_temp_hub"))

    # create temp hub on client 1
    client_1_interfaces = requests.get(f"{scenario_data.client_1_api_endpoint}/api/wg/interfaces", verify=False, auth=HTTPBasicAuth("wg_spoke", "wg_spoke")).json()[0]
    requests.post(f"{scenario_data.client_1_api_endpoint}/api/wg/interface/peers", json={
        "public_key": "KMFZz2cUuQx0Equ6ITTJOTt1qB/WFR8C/Yw7oYXsSAE=",
        "friendly_name": "temp hub",
        "description": "",
        "persistent_keepalives": 5,
        "preshared_key": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
        "endpoint": "wg_temp_hub:51819",
        "cidr_routes": "172.29.0.16/28, fd00::1:0/112",
        "wg_interface_id": client_1_interfaces["instance_id"]
    }, verify=False, auth=HTTPBasicAuth("wg_spoke", "wg_spoke"))

    # create peer on perm hub for client 2
    perm_hub_interfaces = requests.get(f"{scenario_data.hub_api_endpoint}/api/wg/interfaces", verify=False, auth=HTTPBasicAuth("wg_hub", "wg_hub")).json()
    requests.post(f"{scenario_data.hub_api_endpoint}/api/wg/interface/peers", json={
        # Private key 8H/dSh/s2sb1rOUiERJPLci+ggYCWhMaNViTmdC3rX4=
        "public_key": "BOfvfui5k0KeGM8uVDf5jAcmCmM4i9Rk8URU+tkXwyI=",
        "friendly_name": "Client 2",
        "description": "",
        "preshared_key": "VAh4Pvn05h9BM4wniYGr00FQYu7Lq8tCgh8YpxpaC8Y=",
        "endpoint": "",
        "cidr_routes": "172.29.1.32/32, fd00:1::32/128",
        "wg_interface_id": [x for x in perm_hub_interfaces if x["intf_name"] == "wg16"][0]["instance_id"]
    }, verify=False, auth=HTTPBasicAuth("wg_hub", "wg_hub"))

def destroy_scenario_2():
    """destroy scenario 1 container and networks
    """
    scenario_data = ScenarioTwoData()
    client = docker.from_env()

    client.containers.list(filters={"name": "nginx_demo_temp"})[0].remove(force=True)
    client.containers.list(filters={"name": "nginx_demo"})[0].remove(force=True)
    client.containers.list(filters={"name": "wg_client_1"})[0].remove(force=True)
    client.containers.list(filters={"name": "wg_temp_hub"})[0].remove(force=True)
    client.containers.list(filters={"name": "wg_hub"})[0].remove(force=True)
    client.networks.list(names="wg_transit_temp")[0].remove()
    client.networks.list(names="wg_transit")[0].remove()
    client.networks.list(names="wg_public_transit")[0].remove()
    client.networks.list(names="wg_public")[0].remove()
    shutil.rmtree(scenario_data.tmp_dir_base)
