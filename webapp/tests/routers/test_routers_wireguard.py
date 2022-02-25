"""
test rules API endpoints
"""
import pytest
from fastapi.testclient import TestClient

import models


@pytest.mark.usefixtures("disable_os_level_commands")
class TestWgInterfaceApi:
    """
    Test WgInterfaceModel API
    """
    list_api_endpoint = "/api/wg/interfaces"
    detail_api_endpoint = "/api/wg/interfaces/{instance_id}"

    async def test_get_endpoint(self, test_client: TestClient, clean_db):
        """
        get WgInterface API endpoint
        """
        for e in range(1, 10):
            await models.WgInterfaceModel.create(
                intf_name=f"wg{e}",
                listen_port=51820+e,
                cidr_addresses=f"192.168.1.{e}/32",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )

        # fetch through API
        response = await test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text

        data = response.json()
        assert len(data) == 9

        response = await test_client.get(self.detail_api_endpoint.format(instance_id=data[0]["instance_id"]))
        assert response.status_code == 200, response.text

        json_data = response.json()
        assert json_data == data[0]
        assert "private_key" not in data[0].keys()

    async def test_crud(self, test_client: TestClient, clean_db):
        """
        test CRUD operations on API endpoint
        """
        # create through API
        response = await test_client.post(self.list_api_endpoint, json={
            "intf_name": "wgvpn1",
            "cidr_addresses": "192.168.1.1/32",
            "private_key": "cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        })
        assert response.status_code == 200, response.text

        # fetch created entry from DB
        data = response.json()
        wim = await models.WgInterfaceModel.get(
            instance_id=data["instance_id"]
        )

        # update through API (just change the port number)
        response = await test_client.put(self.detail_api_endpoint.format(instance_id=data["instance_id"]), json={
            "intf_name": "wgvpn1",
            "cidr_addresses": "192.168.1.1/32",
            "private_key": "cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=",
            "listen_port": 51830
        })
        assert response.status_code == 200, response.text
        wim = await models.WgInterfaceModel.get(
            instance_id=data["instance_id"]
        )
        assert wim.listen_port == 51830

        # delete through API
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id=data["instance_id"]))
        assert response.status_code == 200
        assert await models.WgInterfaceModel.all().count() == 0

    async def test_delete_with_invalid_id(self, test_client: TestClient):
        """test delete with invalid id"""
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id="NotExist"))
        assert response.status_code == 404

    async def test_invalid_input_on_generic_field(self, test_client: TestClient):
        """
        test post call with invalid data
        """
        response = await test_client.post(self.list_api_endpoint, json={
            "intf_name": "wgvpn1",
            "cidr_addresses": "192.168.1.1/32",
            "listen_port": 98765432345678,
            "private_key": "cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        })
        assert response.status_code == 422, response.text

        data = response.json()
        assert data["detail"] == [
            {
                "ctx": {"limit_value": 2147483647},
                "loc": ["body",
                        "listen_port"],
                "msg": "ensure this value is less than or equal to 2147483647",
                "type": "value_error.number.not_le"
            }
        ]

    async def test_wireguard_interface_reconfigure(self, test_client: TestClient, clean_db):
        """test reconfigure API call
        """
        # create through API
        response = await test_client.post(self.list_api_endpoint, json={
            "intf_name": "wgvpn1",
            "cidr_addresses": "192.168.1.1/32",
            "private_key": "cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        })
        assert response.status_code == 200, response.text
        data = response.json()

        response = await test_client.post(
            self.detail_api_endpoint.format(
                instance_id=data["instance_id"]
            ) + "/reconfigure",
            json={}
        )
        assert response.status_code == 200, response.text
        assert response.json()["message"] == "configuration applied"


@pytest.mark.usefixtures("disable_os_level_commands")
class TestWgPeerApi:
    """
    Test WgPeer API endpoints
    """
    list_api_endpoint = "/api/wg/interface/peers"
    detail_api_endpoint = "/api/wg/interface/peers/{instance_id}"

    async def test_get_peers(self, test_client: TestClient, clean_db):
        """
        get peer list
        """
        wgintf = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )

        peer = await models.WgPeerModel.create(
            wg_interface=wgintf,
            public_key="6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=",
            cidr_routes="10.1.1.3/32"
        )

        # fetch list through API
        response = await test_client.get(self.list_api_endpoint)
        assert response.status_code == 200, response.text

        data = response.json()
        assert len(data) == 1

        # test get peer
        response = await test_client.get(self.detail_api_endpoint.format(instance_id=data[0]["instance_id"]))
        assert response.status_code == 200, response.text

        json_data = response.json()
        assert json_data == data[0]

    async def test_get_is_active_peer(self, test_client: TestClient, clean_db):
        wgintf = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )

        peer = await models.WgPeerModel.create(
            wg_interface=wgintf,
            public_key="6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=",
            cidr_routes="10.1.1.3/32"
        )

        # fetch list through API
        response = await test_client.get(self.detail_api_endpoint.format(instance_id=str(peer.instance_id)) + "/is_active")
        assert response.status_code == 200, response.text

        data = response.json()
        assert data == {
            "active": False
        }

    async def test_create_update_peer(self, test_client: TestClient, clean_db):
        """test create on API endpoint
        """
        wgintf = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )
        response = await test_client.post(self.list_api_endpoint, json={
            "cidr_routes": "10.1.1.3/32",
            "public_key": "cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=",
            "endpoint": "1.1.1.1:51820",
            "wg_interface_id": str(wgintf.instance_id)
        })
        assert response.status_code == 200, response.text

        # fetch created entry from DB
        data = response.json()
        obj = await models.WgPeerModel.get(
            instance_id=data["instance_id"]
        )
        await obj.fetch_related("wg_interface")
        assert obj.wg_interface.instance_id == wgintf.instance_id

        # update entry
        response = await test_client.put(self.detail_api_endpoint.format(instance_id=data["instance_id"]), json={
            "public_key": "cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=",
            "cidr_routes": "10.1.1.3/32",
            "endpoint": "2.2.2.2:51820",
            "wg_interface_id": str(wgintf.instance_id)
        })
        assert response.status_code == 200, response.text
        obj = await models.WgPeerModel.get(
            instance_id=data["instance_id"]
        )
        assert obj.endpoint == "2.2.2.2:51820"

    async def test_delete_peer(self, test_client: TestClient, clean_db):
        """test delete of peer
        """
        wgintf = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )
        peer = await models.WgPeerModel.create(
            wg_interface=wgintf,
            public_key="6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=",
            cidr_routes="10.1.1.3/32"
        )

        response = await test_client.delete(self.detail_api_endpoint.format(instance_id=peer.instance_id))
        assert response.status_code == 200
        assert await models.WgPeerModel.all().count() == 0

    async def test_delete_peer_with_invalid_id(self, test_client: TestClient, clean_db):
        """test delete with invlaid ID
        """
        response = await test_client.delete(self.detail_api_endpoint.format(instance_id="IdNotFound"))
        assert response.status_code == 404
