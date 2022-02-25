"""
test app.wg module
"""
import os
import json

import pytest
from fastapi.testclient import TestClient

import app.wg_config_adapter
import models
import utils.os_func


@pytest.mark.usefixtures("disable_os_level_commands")
class TestWgConfigAdapter:
    """
    Test WgConfigAdapter
    """
    async def _create_test_data(self, prl: models.PolicyRuleListModel):
        """create test data for the class"""
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            protocol=models.FilterProtocolEnum.TCP,
            dst_port_number=3000
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24"
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            action=models.IpTableActionEnum.ACCEPT
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            table=models.IpTableNameEnum.INPUT
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            except_src=True,
            except_dst=True
        )
        await models.Ipv6FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="2001:DB8:0::/64",
            dst_network="2001:DB8:1::/64"
        )
        await models.Ipv4NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth1"
        )
        await models.Ipv6NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth8"
        )

    async def test_is_initialized(self, test_client: TestClient, clean_db):
        """
        test configuration of a wireguard interface through the adapter
        """
        instance = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )
        obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
        # make sure that the configuration file does not exist
        os.remove(obj._config_path)

        assert obj.is_initialized() is False
        assert obj.get_config() == ""

        await obj.init_config()
        assert obj.is_initialized() is True
        assert obj.get_config() != ""

        os.remove(obj._config_path)
        assert obj.is_initialized() is False

    async def test_interface_exists(self, test_client: TestClient, clean_db, monkeypatch):
        """test interface exists method
        """
        def mock_wg_json_command(command: str, **kwargs):
            data = {
                "wgvpn16": {
                        "privateKey": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
                        "publicKey": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
                        "listenPort": 51820,
                        "peers": {}
                }
            }
            return json.dumps(data, indent=4), "", True

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command)

            instance = await models.WgInterfaceModel.create(
                intf_name="wgvpn16",
                listen_port=51820,
                cidr_addresses="10.1.1.1/24",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )
            obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
            await obj.init_config()
            assert await obj.interface_exists() is True

            instance = await models.WgInterfaceModel.create(
                intf_name="wg1",
                listen_port=51821,
                cidr_addresses="10.1.1.1/24",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )
            obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
            await obj.init_config()
            assert await obj.interface_exists() is False

    async def test_interface_up(self, test_client: TestClient, clean_db, monkeypatch):
        """test interface up method
        """
        data = {
            "wgvpn16": {
                "privateKey": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
                "publicKey": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
                "listenPort": 51820,
                "peers": {}
            }
        }
        def mock_command_success(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            return "", "", True

        def mock_command_failed(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            return "", "", False

        def mock_command_exception(command: str, **kwargs):
            raise Exception("An Exception")

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_command_success)

            instance = await models.WgInterfaceModel.create(
                intf_name="wg1",
                cidr_addresses="10.1.1.1/24",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )
            obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
            await obj.init_config()
            assert await obj.interface_exists() is False
            assert await obj.interface_up() is True

            m.setattr(utils.os_func, "run_subprocess", mock_command_failed)
            assert await obj.interface_up() is False

            m.setattr(utils.os_func, "run_subprocess", mock_command_exception)
            with pytest.raises(Exception):
                await obj.interface_up() is False

    async def test_interface_down(self, test_client: TestClient, clean_db, monkeypatch):
        """test interface down method
        """
        data = {
            "wgvpn16": {
                "privateKey": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
                "publicKey": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
                "listenPort": 51820,
                "peers": {}
            }
        }
        def mock_command_success(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            return "", "", True

        def mock_command_failed(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            return "", "", False

        def mock_command_exception(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            raise Exception("An Exception")

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_command_success)

            instance = await models.WgInterfaceModel.create(
                intf_name="wgvpn16",
                cidr_addresses="10.1.1.1/24",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )
            obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
            await obj.init_config()
            assert await obj.interface_exists() is True
            assert await obj.interface_down() is True

            m.setattr(utils.os_func, "run_subprocess", mock_command_failed)
            assert await obj.interface_down() is False

            m.setattr(utils.os_func, "run_subprocess", mock_command_exception)
            assert await obj.interface_down() is False

    async def test_base_init_config(self, test_client: TestClient, clean_db):
        """verify base wireguard configuration that is generated from the model
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        await self._create_test_data(prl)
        instance = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=",
            policy_rule_list=prl
        )
        obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
        await obj.init_config()

        expected_configuration = f"""\
# configuration managed by script - please don't change -  ({instance.instance_id})
[Interface]
PrivateKey = cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=
Address = 10.1.1.1/24
ListenPort = 51820
Table = auto
PostUp = iptables --append FORWARD --in-interface %i --protocol tcp --dport 3000 --jump DROP; iptables --append FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP; iptables --append FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump ACCEPT; iptables --append INPUT --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP; iptables --append FORWARD --in-interface %i ! --source 192.168.1.0/24 ! --destination 192.168.2.0/24 --jump DROP; iptables --append POSTROUTING --table nat --out-interface eth1 --jump MASQUERADE
PostUp = ip6tables --append FORWARD --in-interface %i --source 2001:DB8:0::/64 --destination 2001:DB8:1::/64 --jump DROP; ip6tables --append POSTROUTING --table nat --out-interface eth8 --jump MASQUERADE
PostDown = iptables --delete FORWARD --in-interface %i --protocol tcp --dport 3000 --jump DROP; iptables --delete FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP; iptables --delete FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump ACCEPT; iptables --delete INPUT --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP; iptables --delete FORWARD --in-interface %i ! --source 192.168.1.0/24 ! --destination 192.168.2.0/24 --jump DROP; iptables --delete POSTROUTING --table nat --out-interface eth1 --jump MASQUERADE
PostDown = ip6tables --delete FORWARD --in-interface %i --source 2001:DB8:0::/64 --destination 2001:DB8:1::/64 --jump DROP; ip6tables --delete POSTROUTING --table nat --out-interface eth8 --jump MASQUERADE
"""

        assert obj.get_config() == expected_configuration

    async def test_rebuild_peer_config(self, test_client: TestClient, clean_db):
        """verify rebuild of the peer configuration
        """
        instance = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )
        peer_a = await models.WgPeerModel.create(
            wg_interface=instance,
            public_key="6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=",
            cidr_routes="10.1.1.3/32",
            endpoint="10.1.1.1:51820",
            persistent_keepalives=10,
            preshared_key="SscYJqiFCncZVzYAiW6X7DUeE8TiGHS0MULu6pUMiYc="
        )
        obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
        await obj.init_config()

        expected_configuration = f"""\
# configuration managed by script - please don't change -  ({instance.instance_id})
[Interface]
PrivateKey = cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=
Address = 10.1.1.1/24
ListenPort = 51820
Table = auto

# {peer_a.instance_id} / None / \n[Peer]
PublicKey = 6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=
AllowedIPs = 10.1.1.3/32
Endpoint = 10.1.1.1:51820
PersistentKeepalive = 10
PresharedKey = SscYJqiFCncZVzYAiW6X7DUeE8TiGHS0MULu6pUMiYc=
"""
        assert obj.get_config() == expected_configuration

        peer_b = await models.WgPeerModel.create(
            wg_interface=instance,
            public_key="aKFcOzSjFPHaX4dX3RteK1ziDFKOdAyy4FcReJa6MX8=",
            cidr_routes="10.1.1.4/32"
        )

        # rebuild peer configuration is called as part of the peer signal after creation
        #await obj.rebuild_peer_config()
        expected_configuration = f"""\
# configuration managed by script - please don't change -  ({instance.instance_id})
[Interface]
PrivateKey = cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=
Address = 10.1.1.1/24
ListenPort = 51820
Table = auto

# {peer_a.instance_id} / None / \n[Peer]
PublicKey = 6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=
AllowedIPs = 10.1.1.3/32
Endpoint = 10.1.1.1:51820
PersistentKeepalive = 10
PresharedKey = SscYJqiFCncZVzYAiW6X7DUeE8TiGHS0MULu6pUMiYc=

# {peer_b.instance_id} / None / \n[Peer]
PublicKey = aKFcOzSjFPHaX4dX3RteK1ziDFKOdAyy4FcReJa6MX8=
AllowedIPs = 10.1.1.4/32
"""
        assert obj.get_config() == expected_configuration

    async def test_apply_config(self, test_client: TestClient, clean_db, monkeypatch):
        """test wireguard apply config on OS level
        """
        data = {
            "wgvpn16": {
                "privateKey": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
                "publicKey": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
                "listenPort": 51820,
                "peers": {}
            }
        }
        def mock_command_success(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            return "", "", True

        def mock_command_failed_wg_strip(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            elif command.startswith("wg-quick strip"):
                return "", "", False

        def mock_command_failed_wg_syncconf(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            elif command.startswith("wg syncconf"):
                return "", "", False

            return "", "", True

        def mock_command_exception(command: str, **kwargs):
            if command == "wg-json":
                return json.dumps(data, indent=4), "", True

            raise Exception("An Exception")

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_command_success)
            instance = await models.WgInterfaceModel.create(
                intf_name="wgvpn16",
                cidr_addresses="10.1.1.1/24",
                private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
            )
            obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
            await obj.init_config()
            assert await obj.apply_config() is True

            m.setattr(utils.os_func, "run_subprocess", mock_command_failed_wg_strip)
            assert await obj.apply_config() is False

            m.setattr(utils.os_func, "run_subprocess", mock_command_failed_wg_syncconf)
            assert await obj.apply_config() is False

            # call with recreate
            m.setattr(utils.os_func, "run_subprocess", mock_command_success)
            assert await obj.apply_config(recreate_interface=True) is True

            m.setattr(utils.os_func, "run_subprocess", mock_command_success)
            assert await obj.apply_config(recreate_interface=True) is True

            # test failure scenario
            m.setattr(utils.os_func, "run_subprocess", mock_command_exception)
            assert await obj.apply_config() is False
            assert await obj.apply_config(recreate_interface=True) is False

    async def test_delete_config(self, test_client: TestClient, clean_db, monkeypatch):
        """test delete wireguard configuration
        """
        instance = await models.WgInterfaceModel.create(
            intf_name="wg1",
            cidr_addresses="10.1.1.1/24",
            private_key="cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI="
        )
        peer_a = await models.WgPeerModel.create(
            wg_interface=instance,
            public_key="6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=",
            cidr_routes="10.1.1.3/32"
        )
        obj = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)
        await obj.init_config()

        expected_configuration = f"""\
# configuration managed by script - please don't change -  ({instance.instance_id})
[Interface]
PrivateKey = cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=
Address = 10.1.1.1/24
ListenPort = 51820
Table = auto

# {peer_a.instance_id} / None / \n[Peer]
PublicKey = 6Prv1yQ2Fh99Xhi4eUmPZnGox0VrLH88MFtdNXfM52E=
AllowedIPs = 10.1.1.3/32
"""
        assert obj.get_config() == expected_configuration

        await obj.delete_config()

        assert obj.get_config() == ""
