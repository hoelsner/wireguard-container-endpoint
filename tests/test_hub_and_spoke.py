"""
test scenario 1
"""
import logging
import time

import docker
import pytest
import requests
import requests.packages
from urllib3.exceptions import InsecureRequestWarning

import utils


@pytest.mark.usefixtures("use_scenario_1")
class TestHubAndSpokeScenario:
    """
    test hub-and-spoke scenario according to docs/scenarios/scenario_1
    """
    scen_data = utils.ScenarioOneData()
    healthcheck_endpoint = "/api/healthcheck/"
    instance_info_endpoint = "/api/utils/instance/info"
    interface_endpoint = "/api/wg/interfaces"
    peers_endpoint = "/api/wg/interface/peers"
    wg_opstate_endpoint = "/api/utils/wg/operational"
    ping_endpoint = "/api/utils/ping/"
    http_get_endpoint = "/api/utils/http/get/"

    def test_container_healthchecks(self, hub_basic_auth, client_basic_auth):
        """verify the state of the containers
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.instance_info_endpoint}", auth=hub_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-1-test",
            "name": "WG Hub",
            "debug": False
        }

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.instance_info_endpoint}", auth=client_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-1-test",
            "name": "WG Client 1",
            "debug": False
        }

    def test_init_peer_is_active(self, hub_basic_auth, client_basic_auth):
        """verify that initial peers are active
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.wg_opstate_endpoint}", auth=hub_basic_auth, verify=False)
        assert response.status_code == 200
        data = response.json()
        assert "wg16" in data.keys()
        assert "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=" in data["wg16"]["peers"].keys()

        peer_data = data["wg16"]["peers"]["s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs="]
        assert "latestHandshake" in peer_data.keys()
        assert peer_data["transferRx"] > 10
        assert peer_data["transferTx"] > 10

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.wg_opstate_endpoint}", auth=client_basic_auth, verify=False)
        assert response.status_code == 200
        data = response.json()
        assert "wg15" in data.keys()
        assert "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=" in data["wg15"]["peers"].keys()

        peer_data = data["wg15"]["peers"]["yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k="]
        assert "latestHandshake" in peer_data.keys()
        assert peer_data["transferRx"] > 10
        assert peer_data["transferTx"] > 10

    def test_reachability_between_hub_and_spoke(self, client_basic_auth):
        """test reachability from spoke to hub
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        for target in self.scen_data.hub_ping_endpoints:
            response = requests.post(
                f"{self.scen_data.client_1_api_endpoint}{self.ping_endpoint}{target}",
                auth=client_basic_auth,
                verify=False
            )
            assert response.status_code == 200, f"Failed to send data to: {self.scen_data.client_1_api_endpoint}{self.ping_endpoint}{target}"
            data = response.json()
            logging.info(data)
            assert data["success"] is True, f"Failed to send data to: {target}"

        # test service reachability
        targets = [
            self.scen_data.http_ipv4_endpoint,
            self.scen_data.http_ipv6_endpoint,
            self.scen_data.alt_http_ipv4_endpoint,
            self.scen_data.alt_http_ipv6_endpoint,
        ]
        for target_url in targets:
            response = requests.post(
                f"{self.scen_data.client_1_api_endpoint}{self.http_get_endpoint}",
                json={
                    "url": target_url,
                    "ssl_verify": False
                },
                auth=client_basic_auth,
                verify=False
            )
            assert response.status_code == 200, target_url
            assert response.json()["status"] == 200, target_url

    def test_admin_connectivity(self, hub_basic_auth, client_basic_auth):
        """verify that the access to admin interface is not possible
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        # from client to hub, no connectivtiy is possible
        response = requests.post(
            f"{self.scen_data.client_1_api_endpoint}{self.http_get_endpoint}",
            json={
                "url": self.scen_data.hub_admin_endpoint,
                "ssl_verify": False
            },
            auth=client_basic_auth,
            verify=False
        )
        assert response.status_code == 200
        assert response.json()["status"] == 500, response.json()

        # from hub to client, a connection is possible
        data = {
            "url": self.scen_data.client_1_admin_endpoint,
            "ssl_verify": False
        }
        logging.info(data)
        response = requests.post(
            f"{self.scen_data.hub_api_endpoint}{self.http_get_endpoint}",
            json=data,
            auth=hub_basic_auth,
            verify=False
        )
        assert response.status_code == 200
        assert response.json()["status"] == 404, response.json()

    def test_container_restart(self, hub_basic_auth, client_basic_auth):
        """test that the connectivity is still re-established after reboot
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        client = docker.from_env()
        hub_contianer = client.containers.list(filters={"name": "wg_hub"})[-1]
        hub_contianer.restart()
        time.sleep(30)

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.wg_opstate_endpoint}", auth=hub_basic_auth, verify=False)
        assert response.status_code == 200
        data = response.json()
        assert "wg16" in data.keys()
        assert "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=" in data["wg16"]["peers"].keys()

        peer_data = data["wg16"]["peers"]["s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs="]
        assert "latestHandshake" in peer_data.keys()
        assert peer_data["transferRx"] > 10
        assert peer_data["transferTx"] > 10

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.wg_opstate_endpoint}", auth=client_basic_auth, verify=False)
        assert response.status_code == 200
        data = response.json()
        assert "wg15" in data.keys()
        assert "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=" in data["wg15"]["peers"].keys()

        peer_data = data["wg15"]["peers"]["yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k="]
        assert "latestHandshake" in peer_data.keys()
        assert peer_data["transferRx"] > 10
        assert peer_data["transferTx"] > 10

    def test_add_new_peer_to_hub(self, hub_basic_auth, client_basic_auth):
        """test the deployment of a new peer on the hub and verify the connection to it
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        # create new peer on hub
        response = requests.get(
            f"{self.scen_data.hub_api_endpoint}{self.interface_endpoint}",
            auth=hub_basic_auth,
            verify=False
        )
        assert response.status_code == 200

        wg_interfaces = response.json()
        test_peer = "jqLie8//YQlWlefwJ5VjLpTQxIr0Phb7GOwhYQz8iDM="
        logging.debug(wg_interfaces)
        new_peer_data = {
            "public_key": test_peer,
            "friendly_name": "new client",
            "description": "a new client for the hub",
            "preshared_key": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
            "cidr_routes": "172.29.1.18/32, fd00:1::18/128",
            "wg_interface_id": wg_interfaces[-1]["instance_id"]
        }

        # check if peer already exist
        response = requests.get(
            f"{self.scen_data.hub_api_endpoint}{self.peers_endpoint}",
            json=new_peer_data,
            auth=hub_basic_auth,
            verify=False
        )
        assert response.status_code == 200
        peer_pubkeys = [x["public_key"] for x in response.json()]

        if test_peer not in peer_pubkeys:
            response = requests.post(
                f"{self.scen_data.hub_api_endpoint}{self.peers_endpoint}",
                json=new_peer_data,
                auth=hub_basic_auth,
                verify=False
            )
            assert response.status_code == 200
            time.sleep(2)

        # verify that peer was not active
        response = requests.get(
            f"{self.scen_data.hub_api_endpoint}{self.wg_opstate_endpoint}",
            auth=hub_basic_auth,
            verify=False
        )
        assert response.status_code == 200

        data = response.json()
        assert "wg16" in data.keys()
        assert test_peer in data["wg16"]["peers"].keys()

        peer_data = data["wg16"]["peers"][test_peer]
        assert "latestHandshake" not in peer_data.keys()

        # create client endpoint as container
        scenario_data = utils.ScenarioOneData()
        client = docker.from_env()
        wg_public_network = client.networks.list(filters={"name": "wg_public"})[0]

        wg_client_2_container = client.containers.create(
            image=f"{scenario_data.image_name}:{scenario_data.image_tag}",
            detach=True,
            ports={
                "8002/tcp": ("0.0.0.0", 8002)
            },
            cap_add=["NET_ADMIN", "NET_RAW"],
            environment={
                "DEBUG": "False",
                "APP_NAME": "WG Client 2",
                "APP_PORT": "8002",
                "APP_VERSION": "scenario-2-test",
                "APP_ADMIN_USER": "wg_spoke",
                "APP_ADMIN_PASSWORD": "wg_spoke",
                "LOG_LEVEL": "info",
                # initial configuration
                "INIT_INTF_NAME": "wg14",
                "INIT_INTF_LISTEN_PORT": "51822",
                "INIT_INTF_PRIVATE_KEY": "IPc3vDCw4i1ZRbfqoNk1+2PgQkZ948Pm1jKg5QCb70c=",
                "INIT_INTF_CIDR_ADDRESSES": "172.29.1.18/32, fd00:1::18/128",
                "INIT_POLICY_NAT_ENABLE": "False",
                "INIT_POLICY_ALLOW_ADMIN": "True",
                "INIT_PEER_PUBLIC_KEY": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
                "INIT_PEER_PRE_SHARED_KEY": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
                "INIT_PEER_PERSISTENT_KEEPALIVE": "5",
                "INIT_PEER_ENDPOINT": "wg_hub:51820",
                "INIT_PEER_CIDR_ROUTES": "172.29.0.0/24, 172.29.1.0/24, fd00::/64, fd00:1::/64",
            },
            sysctls={
                "net.ipv4.ip_forward": "1",
                "net.ipv4.conf.all.src_valid_mark": "1",
                "net.ipv6.conf.all.forwarding": "1",
                "net.ipv6.conf.all.disable_ipv6": "0",
            },
            name="wg_client_2"
        )
        wg_public_network.connect(wg_client_2_container)
        wg_client_2_container.start()
        time.sleep(30)

        # verify that the new peer is active
        response = requests.get(
            f"{self.scen_data.hub_api_endpoint}{self.wg_opstate_endpoint}",
            auth=hub_basic_auth,
            verify=False
        )
        assert response.status_code == 200

        data = response.json()
        assert "wg16" in data.keys()
        assert test_peer in data["wg16"]["peers"].keys()

        peer_data = data["wg16"]["peers"][test_peer]
        assert "latestHandshake" in peer_data.keys()

        # test service reachability
        targets = [
            self.scen_data.http_ipv4_endpoint,
            self.scen_data.http_ipv6_endpoint,
            self.scen_data.alt_http_ipv4_endpoint,
            self.scen_data.alt_http_ipv6_endpoint,
        ]
        for target_url in targets:
            response = requests.post(
                f"https://localhost:8002{self.http_get_endpoint}",
                json={
                    "url": target_url,
                    "ssl_verify": False
                },
                auth=client_basic_auth,
                verify=False
            )
            assert response.status_code == 200, target_url
            assert response.json()["status"] == 200, target_url

        # remove container
        wg_client_2_container.remove(force=True)
