"""
test scenario 2
"""
import time
import pytest
import requests
import requests.packages
from urllib3.exceptions import InsecureRequestWarning

import utils


@pytest.mark.usefixtures("use_scenario_2")
class TestDualHomedClientConnectivity:
    """
    test partial-mesh scenario according to docs/scenarios/scenario_2 with a client that is connected to the
    permanent and temporary hub
    """
    scen_data = utils.ScenarioTwoData()
    healthcheck_endpoint = "/api/healthcheck/"
    instance_info_endpoint = "/api/utils/instance/info"
    interface_endpoint = "/api/wg/interfaces"
    peers_endpoint = "/api/wg/interface/peers"
    wg_opstate_endpoint = "/api/utils/wg/operational"
    ping_endpoint = "/api/utils/ping/"
    http_get_endpoint = "/api/utils/http/get/"

    def test_container_healthchecks(self, hub_basic_auth, client_basic_auth, temp_hub_basic_auth):
        """
        verify the state of the containers
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.instance_info_endpoint}", auth=hub_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Perm Hub",
            "debug": False
        }

        response = requests.get(f"{self.scen_data.temp_hub_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.temp_hub_api_endpoint}{self.instance_info_endpoint}", auth=temp_hub_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Temp Hub",
            "debug": False
        }

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.instance_info_endpoint}", auth=client_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Client 1",
            "debug": False
        }

    def test_dual_homed_client_connectivity(self, client_basic_auth, temp_hub_basic_auth):
        """
        verify, that the client is able to connect to the services on both hubs
        """
        # update endpoint configuration
        response = requests.get(
            f"{self.scen_data.temp_hub_api_endpoint}/api/wg/interfaces",
            verify=False,
            auth=temp_hub_basic_auth
        )
        wg14_interface = [x for x in response.json() if x["intf_name"] == "wg14"][0]

        # create temp hub on client 1
        client_1_interfaces = requests.get(
            f"{self.scen_data.client_1_api_endpoint}/api/wg/interfaces",
            verify=False,
            auth=client_basic_auth
        ).json()[0]
        requests.post(f"{self.scen_data.client_1_api_endpoint}/api/wg/interface/peers", json={
            "public_key": "KMFZz2cUuQx0Equ6ITTJOTt1qB/WFR8C/Yw7oYXsSAE=",
            "friendly_name": "temp hub",
            "description": "",
            "persistent_keepalives": 5,
            "preshared_key": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
            "endpoint": "wg_temp_hub:51819",
            "cidr_routes": "172.29.0.16/28, fd00::1:0/112",
            "wg_interface_id": client_1_interfaces["instance_id"]
        }, verify=False, auth=client_basic_auth)

        # create client entry on temporary hub
        requests.post(f"{self.scen_data.temp_hub_api_endpoint}/api/wg/interface/peers", json={
            "public_key": "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=",
            "friendly_name": "client 1",
            "description": "",
            "persistent_keepalives": 5,
            "preshared_key": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
            "endpoint": "",
            "cidr_routes": "172.29.1.16/32, FD00:1::16/128",
            "wg_interface_id": wg14_interface["instance_id"]
        }, verify=False, auth=temp_hub_basic_auth)
        time.sleep(10)

        # verify connectivity
        targets = [
            self.scen_data.http_ipv4_endpoint,
            self.scen_data.http_ipv6_endpoint,
            self.scen_data.alt_http_ipv4_endpoint,
            self.scen_data.alt_http_ipv6_endpoint,
            self.scen_data.temp_http_ipv4_endpoint,
            self.scen_data.temp_http_ipv6_endpoint,
            self.scen_data.temp_alt_http_ipv4_endpoint,
            self.scen_data.temp_alt_http_ipv6_endpoint,
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


@pytest.mark.usefixtures("use_scenario_2")
class TestSingleHomeConnectivity:
    """
    test partial-mesh scenario according to docs/scenarios/scenario_2 with a client that is only configured
    to connect to the permanent hub (test routing through permanent hub)
    """
    scen_data = utils.ScenarioTwoData()
    healthcheck_endpoint = "/api/healthcheck/"
    instance_info_endpoint = "/api/utils/instance/info"
    interface_endpoint = "/api/wg/interfaces"
    peers_endpoint = "/api/wg/interface/peers"
    wg_opstate_endpoint = "/api/utils/wg/operational"
    ping_endpoint = "/api/utils/ping/"
    http_get_endpoint = "/api/utils/http/get/"

    def test_container_healthchecks(self, hub_basic_auth, client_basic_auth, temp_hub_basic_auth):
        """
        verify the state of the containers
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.instance_info_endpoint}", auth=hub_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Perm Hub",
            "debug": False
        }

        response = requests.get(f"{self.scen_data.temp_hub_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.temp_hub_api_endpoint}{self.instance_info_endpoint}", auth=temp_hub_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Temp Hub",
            "debug": False
        }

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.instance_info_endpoint}", auth=client_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Client 1",
            "debug": False
        }

    def test_single_homed_client_connectivity(self, client_basic_auth):
        """
        verify, that the client is able to connect to the services on both hubs.

        scenario 2 is by default with a single home client connection
        """
        # verify connectivity
        targets = [
            self.scen_data.http_ipv4_endpoint,
            self.scen_data.http_ipv6_endpoint,
            self.scen_data.alt_http_ipv4_endpoint,
            self.scen_data.alt_http_ipv6_endpoint,
            self.scen_data.temp_http_ipv4_endpoint,
            self.scen_data.temp_http_ipv6_endpoint,
            self.scen_data.temp_alt_http_ipv4_endpoint,
            self.scen_data.temp_alt_http_ipv6_endpoint,
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


@pytest.mark.usefixtures("use_scenario_2")
class TestFailOverOnIncompleteClientConfiguration:
    """
    test partial-mesh scenario according to docs/scenarios/scenario_2 with a client that is only configured
    to connect to the permanent hub (test client activity connection)
    """
    scen_data = utils.ScenarioTwoData()
    healthcheck_endpoint = "/api/healthcheck/"
    instance_info_endpoint = "/api/utils/instance/info"
    interface_endpoint = "/api/wg/interfaces"
    peers_endpoint = "/api/wg/interface/peers"
    wg_opstate_endpoint = "/api/utils/wg/operational"
    ping_endpoint = "/api/utils/ping/"
    http_get_endpoint = "/api/utils/http/get/"

    def test_container_healthchecks(self, hub_basic_auth, client_basic_auth, temp_hub_basic_auth):
        """
        verify the state of the containers
        """
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.hub_api_endpoint}{self.instance_info_endpoint}", auth=hub_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Perm Hub",
            "debug": False
        }

        response = requests.get(f"{self.scen_data.temp_hub_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.temp_hub_api_endpoint}{self.instance_info_endpoint}", auth=temp_hub_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Temp Hub",
            "debug": False
        }

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.healthcheck_endpoint}", verify=False)
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

        response = requests.get(f"{self.scen_data.client_1_api_endpoint}{self.instance_info_endpoint}", auth=client_basic_auth, verify=False)
        assert response.status_code == 200
        assert response.json() == {
            "version": "scenario-2-test",
            "name": "WG Client 1",
            "debug": False
        }

    def test_routing_failover_via_interconnect_for_disconnected_client(self, client_basic_auth, temp_hub_basic_auth):
        """
        verify, that the client is able to connect to the services on both hubs
        """
        # update endpoint configuration
        response = requests.get(
            f"{self.scen_data.temp_hub_api_endpoint}/api/wg/interfaces",
            verify=False,
            auth=temp_hub_basic_auth
        )
        wg14_interface = [x for x in response.json() if x["intf_name"] == "wg14"][0]

        # create client entry on temporary hub
        requests.post(f"{self.scen_data.temp_hub_api_endpoint}/api/wg/interface/peers", json={
            "public_key": "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=",
            "friendly_name": "client 1",
            "description": "",
            "persistent_keepalives": 5,
            "preshared_key": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
            "endpoint": "",
            "cidr_routes": "172.29.1.16/32, FD00:1::16/128",
            "wg_interface_id": wg14_interface["instance_id"]
        }, verify=False, auth=temp_hub_basic_auth)
        time.sleep(10)

        # verify connectivity
        targets = [
            self.scen_data.http_ipv4_endpoint,
            self.scen_data.http_ipv6_endpoint,
            self.scen_data.alt_http_ipv4_endpoint,
            self.scen_data.alt_http_ipv6_endpoint,
            self.scen_data.temp_http_ipv4_endpoint,
            self.scen_data.temp_http_ipv6_endpoint,
            self.scen_data.temp_alt_http_ipv4_endpoint,
            self.scen_data.temp_alt_http_ipv6_endpoint,
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
