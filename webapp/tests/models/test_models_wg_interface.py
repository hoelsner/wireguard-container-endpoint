"""
test models.wg_interface module
"""
import pytest

from fastapi.testclient import TestClient
from tortoise.exceptions import ValidationError, IntegrityError

import models


class TestWgInterfaceModel():
    """
    Test WgInterfaceModel
    """
    async def test_base_object_defaults(self, test_client: TestClient, clean_db):
        """test basic use of the model class"""
        obj = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )
        assert obj.listen_port == 51820
        assert obj.policy_rule_list is None
        assert obj.description == ""
        assert obj.private_key is not None, "a random key is generated"
        assert obj.table == models.WgInterfaceTableEnum.AUTO

    async def test_base_object_defaults_with_multiple_cidr_addresses(self, test_client: TestClient, clean_db):
        """test basic use of the model class"""
        obj = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )
        await obj.fetch_related("policy_rule_list")
        assert obj.listen_port == 51820
        assert obj.policy_rule_list is None
        assert obj.description == ""
        assert obj.private_key is not None, "a random key is generated"
        assert obj.table == models.WgInterfaceTableEnum.AUTO

        addresses = obj.cidr_addresses_list
        assert isinstance(addresses, list)
        assert len(addresses) == 1
        assert addresses == [ "10.1.1.1/24" ]

        addresses.append("FE80::2/64")
        obj.cidr_addresses_list = addresses
        adr = obj.cidr_addresses_list
        assert isinstance(adr, list)
        assert len(adr) == 2
        assert adr == [ "10.1.1.1/24", "FE80::2/64" ]

    async def test_private_public_key(self, test_client: TestClient, clean_db):
        """test basic use of the model class"""
        obj = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="kLzhT8mDRys0L+Qc462LhCTOYvM6iT6ycGPOoEu6/Xo="
        )
        assert "4pfjphreRrMpf8ncmFzja7KIiC30OFmebEQneDQ7Mlk=" == obj.public_key

        with pytest.raises(AttributeError):
            obj.public_key = "asdf"

    async def test_cidr_address_validation(self, test_client: TestClient, clean_db):
        """test that an invalid CIDR address will raise a validation error"""
        with pytest.raises(ValidationError) as ex:
            await models.WgInterfaceModel.create(
                intf_name="wg1",
                cidr_addresses="500.1.1.1/24",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )

    async def test_unique_interface_names(self, test_client: TestClient, clean_db):
        """interface name should be unique in configuration"""
        obj = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )

        # interface names must be unique
        with pytest.raises(IntegrityError) as ex:
            await models.WgInterfaceModel.create(
                intf_name="wg1",
                cidr_addresses="10.1.1.2/24",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )

    async def test_unique_listen_port_on_device(self, test_client: TestClient, clean_db):
        """test unique listen_port in configuration"""
        obj = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            listen_port=51821,
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )

        # interface port must be unique within the container
        with pytest.raises(IntegrityError):
            await models.WgInterfaceModel.create(
                intf_name="wgvpn2",
                cidr_addresses="10.1.1.1/24",
                listen_port=51821,
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )

    async def test_invalid_name(self, test_client: TestClient, clean_db):
        """test invalid interface names"""
        obj = await models.WgInterfaceModel.create(
            intf_name="-inspec_123456",
            cidr_addresses="10.1.1.1/32",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )

        # interface name must match specific pattern
        test_value = "awo8ghflwrhgz2iugftudziwuegafktuwuegfvuwke"
        with pytest.raises(ValidationError) as ex:
            await models.WgInterfaceModel.create(
                intf_name=test_value,
                cidr_addresses="10.1.1.2/32",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )

        assert ex.match("intf_name: Value '{}' does not match regex".format(test_value))
