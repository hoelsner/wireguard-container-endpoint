"""
test models.peer module
"""
import pytest
from fastapi.testclient import TestClient
from tortoise.exceptions import ValidationError

import models


@pytest.mark.usefixtures("disable_os_level_commands")
class TestWgPeerModel:
    """
    Test WgPeerModel model
    """
    async def test_basic_model(self, test_client: TestClient):
        """test basic data model operations
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

        assert peer.friendly_name is None
        assert peer.description == ""
        assert peer.persistent_keepalives == -1
        assert peer.preshared_key is None
        assert peer.endpoint is None
        assert str(peer) == str("6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=")

        peer.friendly_name = "Name"
        assert str(peer) == str("Name (6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=)")

        routes = peer.cidr_routes_list
        assert isinstance(routes, list)
        assert len(routes) == 1
        assert routes == [ "10.1.1.3/32" ]

        routes.append("FE80::2/128")
        peer.cidr_routes_list = routes
        adr = peer.cidr_routes_list
        assert isinstance(adr, list)
        assert len(adr) == 2
        assert adr == [ "10.1.1.3/32", "FE80::2/128" ]

        with pytest.raises(ValidationError):
            await models.WgPeerModel.create(
                wg_interface=wgintf,
                public_key="6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=",
                cidr_routes="10.1.1.3/32",
                friendly_name="###_--++$$"
            )

    async def test_peer_without_route(self, test_client: TestClient):
        """ensure that every peer has at least a single allowed IP statement (at least the remote IP)
        """
        wgintf = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )

        with pytest.raises(ValidationError):
            await models.WgPeerModel.create(
                wg_interface=wgintf,
                public_key="6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=",
                cidr_routes=""
            )
