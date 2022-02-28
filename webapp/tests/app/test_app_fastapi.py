# pylint: missing-function-docstring
import os

import pytest
from fastapi.testclient import TestClient

import app.init_config
import models
import utils.config


@pytest.mark.usefixtures("disable_os_level_commands")
@pytest.mark.usefixtures("skip_init_config")
class TestInitialConfig:
    """test initial configuration wizard
    """
    async def test_missing_trigger_init_config(self, test_client: TestClient, clean_db):
        """check that initial configuration is not triggered if the hostname is undefined
        """
        assert os.environ.get("INIT_INTF_NAME", None) is None
        response = await app.init_config.run()
        assert response is True, "initial configuration was not executed successfully"
        assert await models.WgInterfaceModel.all().count() == 0, "there is no interface created"

    async def test_initial_config_trigger(self, test_client: TestClient, clean_db, monkeypatch):
        """test that initial configuration wizard is triggered with minimal configuration
        """
        with monkeypatch.context() as m:
            monkeypatch.setenv("INIT_INTF_NAME", "wg16", prepend=False)
            monkeypatch.setenv("INIT_INTF_PRIVATE_KEY", "CNpLjY5Hqsul87kPLSEXFxP+6FIU+Te0GsXs3quVbno=", prepend=False)
            monkeypatch.setenv("INIT_INTF_CIDR_ADDRESSES", "10.1.1.1/32, FD00::1/128", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAME", "initial policy", prepend=False)
            monkeypatch.setenv("INIT_PEER_PUBLIC_KEY", "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg=", prepend=False)
            monkeypatch.setenv("INIT_PEER_ENDPOINT", "localhost:51821", prepend=False)
            monkeypatch.setenv("INIT_PEER_CIDR_ROUTES", "10.1.1.254/32, FD00::FFFF/128", prepend=False)

            # verify defaults
            init_config = utils.config.InitConfigUtil()
            assert init_config.intf_listen_port == 51820
            assert init_config.policy_nat_enable is False
            assert init_config.policy_allow_admin is True
            assert init_config.peer_preshared_key is None
            assert init_config.peer_persistent_keepalive == 30

            # run configuration
            response = await app.init_config.run()
            assert response is True
            assert await models.PolicyRuleListModel.all().count() == 1
            assert await models.WgInterfaceModel.all().count() == 1
            assert await models.WgPeerModel.all().count() == 1

            wg_intf = await models.WgInterfaceModel.get(intf_name="wg16").prefetch_related("peers", "policy_rule_list")
            assert wg_intf.intf_name == "wg16"
            assert wg_intf.policy_rule_list is not None
            assert wg_intf.description == "interface created by initial configuration wizard"
            assert wg_intf.listen_port == 51820
            assert wg_intf.private_key == "CNpLjY5Hqsul87kPLSEXFxP+6FIU+Te0GsXs3quVbno="
            assert wg_intf.cidr_addresses == "10.1.1.1/32, FD00::1/128"

            peer = await wg_intf.peers.all().first()
            assert peer.friendly_name == "initial peer"
            assert peer.public_key == "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg="
            assert peer.description == "peer created as initial interface"
            assert peer.persistent_keepalives == 30
            assert peer.preshared_key is None
            assert peer.endpoint == "localhost:51821"
            assert peer.cidr_routes == "10.1.1.254/32, FD00::FFFF/128"

    async def test_initial_config_error(self, test_client: TestClient, clean_db, monkeypatch):
        """test transaction behavior when initial configuration failed
        """
        with monkeypatch.context() as m:
            monkeypatch.setenv("INIT_INTF_NAME", "wg16", prepend=False)
            monkeypatch.setenv("INIT_INTF_PRIVATE_KEY", "+6FIU+Te0GsXs3quVbno=", prepend=False)
            monkeypatch.setenv("INIT_INTF_CIDR_ADDRESSES", "10.1.1.1/32, FD00::1/128", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAME", "initial policy", prepend=False)
            monkeypatch.setenv("INIT_PEER_PUBLIC_KEY", "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg=", prepend=False)
            monkeypatch.setenv("INIT_PEER_ENDPOINT", "localhost:51821", prepend=False)
            monkeypatch.setenv("INIT_PEER_CIDR_ROUTES", "10.1.1.254/32, FD00::FFFF/128", prepend=False)

            # verify defaults
            init_config = utils.config.InitConfigUtil()
            assert init_config.intf_listen_port == 51820
            assert init_config.policy_nat_enable is False
            assert init_config.policy_allow_admin is True
            assert init_config.peer_preshared_key is None
            assert init_config.peer_persistent_keepalive == 30

            # run configuration
            response = await app.init_config.run()
            assert response is False
            assert await models.PolicyRuleListModel.all().count() == 0
            assert await models.WgInterfaceModel.all().count() == 0
            assert await models.WgPeerModel.all().count() == 0

    async def test_initial_config_with_nat(self, test_client: TestClient, clean_db, monkeypatch):
        """test initial configuration with NAT
        """
        with monkeypatch.context() as m:
            monkeypatch.setenv("INIT_INTF_NAME", "wg16", prepend=False)
            monkeypatch.setenv("INIT_INTF_PRIVATE_KEY", "CNpLjY5Hqsul87kPLSEXFxP+6FIU+Te0GsXs3quVbno=", prepend=False)
            monkeypatch.setenv("INIT_INTF_CIDR_ADDRESSES", "10.1.1.1/32, FD00::1/128", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAME", "initial policy", prepend=False)
            monkeypatch.setenv("INIT_PEER_PUBLIC_KEY", "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg=", prepend=False)
            monkeypatch.setenv("INIT_PEER_ENDPOINT", "localhost:51821", prepend=False)
            monkeypatch.setenv("INIT_PEER_CIDR_ROUTES", "10.1.1.254/32, FD00::FFFF/128", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAT_ENABLE", "True", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAT_INTF", "eth0", prepend=False)

            # verify defaults
            init_config = utils.config.InitConfigUtil()
            assert init_config.intf_listen_port == 51820
            assert init_config.policy_nat_enable is True
            assert init_config.policy_allow_admin is True
            assert init_config.peer_preshared_key is None
            assert init_config.peer_persistent_keepalive == 30

            # run configuration
            response = await app.init_config.run()
            assert response is True
            assert await models.PolicyRuleListModel.all().count() == 1
            assert await models.WgInterfaceModel.all().count() == 1
            assert await models.WgPeerModel.all().count() == 1
            assert await models.Ipv4FilterRuleModel.all().count() == 0
            assert await models.Ipv6FilterRuleModel.all().count() == 0
            assert await models.Ipv4NatRuleModel.all().count() == 1
            assert await models.Ipv6NatRuleModel.all().count() == 1

            wg_intf = await models.WgInterfaceModel.get(intf_name="wg16").prefetch_related("peers", "policy_rule_list")
            assert wg_intf.intf_name == "wg16"
            assert wg_intf.policy_rule_list is not None
            assert wg_intf.description == "interface created by initial configuration wizard"
            assert wg_intf.listen_port == 51820
            assert wg_intf.private_key == "CNpLjY5Hqsul87kPLSEXFxP+6FIU+Te0GsXs3quVbno="
            assert wg_intf.cidr_addresses == "10.1.1.1/32, FD00::1/128"

            peer = await wg_intf.peers.all().first()
            assert peer.friendly_name == "initial peer"
            assert peer.public_key == "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg="
            assert peer.description == "peer created as initial interface"
            assert peer.persistent_keepalives == 30
            assert peer.preshared_key is None
            assert peer.endpoint == "localhost:51821"
            assert peer.cidr_routes == "10.1.1.254/32, FD00::FFFF/128"

            rule_list = await wg_intf.policy_rule_list.to_iptables_list()
            exp_rule_list = [
                'iptables --append POSTROUTING --table nat --out-interface eth0 --jump MASQUERADE',
                'ip6tables --append POSTROUTING --table nat --out-interface eth0 --jump MASQUERADE'
            ]
            assert rule_list == exp_rule_list

    async def test_initial_config_with_rule(self, test_client: TestClient, clean_db, monkeypatch):
        """test with deny access to admin interface from VPN
        """
        with monkeypatch.context() as m:
            monkeypatch.setenv("INIT_INTF_NAME", "wg16", prepend=False)
            monkeypatch.setenv("INIT_INTF_PRIVATE_KEY", "CNpLjY5Hqsul87kPLSEXFxP+6FIU+Te0GsXs3quVbno=", prepend=False)
            monkeypatch.setenv("INIT_INTF_CIDR_ADDRESSES", "10.1.1.1/32, FD00::1/128", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAME", "initial policy", prepend=False)
            monkeypatch.setenv("INIT_PEER_PUBLIC_KEY", "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg=", prepend=False)
            monkeypatch.setenv("INIT_PEER_ENDPOINT", "localhost:51821", prepend=False)
            monkeypatch.setenv("INIT_PEER_CIDR_ROUTES", "10.1.1.254/32, FD00::FFFF/128", prepend=False)
            monkeypatch.setenv("INIT_POLICY_ALLOW_ADMIN", "False", prepend=False)

            # verify defaults
            init_config = utils.config.InitConfigUtil()
            assert init_config.intf_listen_port == 51820
            assert init_config.policy_nat_enable is False
            assert init_config.policy_allow_admin is False
            assert init_config.peer_preshared_key is None
            assert init_config.peer_persistent_keepalive == 30

            # run configuration
            response = await app.init_config.run()
            assert response is True
            assert await models.PolicyRuleListModel.all().count() == 1
            assert await models.WgInterfaceModel.all().count() == 1
            assert await models.WgPeerModel.all().count() == 1
            assert await models.Ipv4FilterRuleModel.all().count() == 1
            assert await models.Ipv6FilterRuleModel.all().count() == 1
            assert await models.Ipv4NatRuleModel.all().count() == 0
            assert await models.Ipv6NatRuleModel.all().count() == 0

            wg_intf = await models.WgInterfaceModel.get(intf_name="wg16").prefetch_related("peers", "policy_rule_list")
            assert wg_intf.intf_name == "wg16"
            assert wg_intf.policy_rule_list is not None
            assert wg_intf.description == "interface created by initial configuration wizard"
            assert wg_intf.listen_port == 51820
            assert wg_intf.private_key == "CNpLjY5Hqsul87kPLSEXFxP+6FIU+Te0GsXs3quVbno="
            assert wg_intf.cidr_addresses == "10.1.1.1/32, FD00::1/128"

            peer = await wg_intf.peers.all().first()
            assert peer.friendly_name == "initial peer"
            assert peer.public_key == "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg="
            assert peer.description == "peer created as initial interface"
            assert peer.persistent_keepalives == 30
            assert peer.preshared_key is None
            assert peer.endpoint == "localhost:51821"
            assert peer.cidr_routes == "10.1.1.254/32, FD00::FFFF/128"

            rule_list = await wg_intf.policy_rule_list.to_iptables_list()
            exp_rule_list = [
                'iptables --append INPUT --in-interface %i --protocol tcp --dport 8000 --jump DROP',
                'ip6tables --append INPUT --in-interface %i --protocol tcp --dport 8000 --jump DROP'
            ]
            assert rule_list == exp_rule_list

    async def test_initial_config_with_all_options(self, test_client: TestClient, clean_db, monkeypatch):
        """test init config with all options
        """
        with monkeypatch.context() as m:
            monkeypatch.setenv("INIT_INTF_NAME", "wg16", prepend=False)
            monkeypatch.setenv("INIT_INTF_PRIVATE_KEY", "CNpLjY5Hqsul87kPLSEXFxP+6FIU+Te0GsXs3quVbno=", prepend=False)
            monkeypatch.setenv("INIT_INTF_CIDR_ADDRESSES", "10.1.1.1/32, FD00::1/128", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAME", "initial policy", prepend=False)
            monkeypatch.setenv("INIT_PEER_PUBLIC_KEY", "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg=", prepend=False)
            monkeypatch.setenv("INIT_PEER_ENDPOINT", "localhost:51821", prepend=False)
            monkeypatch.setenv("INIT_PEER_CIDR_ROUTES", "10.1.1.254/32, FD00::FFFF/128", prepend=False)
            monkeypatch.setenv("INIT_POLICY_ALLOW_ADMIN", "False", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAT_ENABLE", "True", prepend=False)
            monkeypatch.setenv("INIT_POLICY_NAT_INTF", "eth0", prepend=False)
            monkeypatch.setenv("INIT_INTF_LISTEN_PORT", "51821", prepend=False)

            # verify defaults
            init_config = utils.config.InitConfigUtil()
            assert init_config.intf_listen_port == 51821
            assert init_config.policy_nat_enable is True
            assert init_config.policy_allow_admin is False
            assert init_config.peer_preshared_key is None
            assert init_config.peer_persistent_keepalive == 30

            # run configuration
            response = await app.init_config.run()
            assert response is True
            assert await models.PolicyRuleListModel.all().count() == 1
            assert await models.WgInterfaceModel.all().count() == 1
            assert await models.WgPeerModel.all().count() == 1
            assert await models.Ipv4FilterRuleModel.all().count() == 1
            assert await models.Ipv6FilterRuleModel.all().count() == 1
            assert await models.Ipv4NatRuleModel.all().count() == 1
            assert await models.Ipv6NatRuleModel.all().count() == 1

            wg_intf = await models.WgInterfaceModel.get(intf_name="wg16").prefetch_related("peers", "policy_rule_list")
            assert wg_intf.intf_name == "wg16"
            assert wg_intf.policy_rule_list is not None
            assert wg_intf.description == "interface created by initial configuration wizard"
            assert wg_intf.listen_port == 51821
            assert wg_intf.private_key == "CNpLjY5Hqsul87kPLSEXFxP+6FIU+Te0GsXs3quVbno="
            assert wg_intf.cidr_addresses == "10.1.1.1/32, FD00::1/128"

            peer = await wg_intf.peers.all().first()
            assert peer.friendly_name == "initial peer"
            assert peer.public_key == "mJhDDD95TPej7RlyfWc+PxK2gzFK/9pyQfLq/hpa2Eg="
            assert peer.description == "peer created as initial interface"
            assert peer.persistent_keepalives == 30
            assert peer.preshared_key is None
            assert peer.endpoint == "localhost:51821"
            assert peer.cidr_routes == "10.1.1.254/32, FD00::FFFF/128"

            rule_list = await wg_intf.policy_rule_list.to_iptables_list()
            exp_rule_list = [
                'iptables --append INPUT --in-interface %i --protocol tcp --dport 8000 --jump DROP',
                'ip6tables --append INPUT --in-interface %i --protocol tcp --dport 8000 --jump DROP',
                'iptables --append POSTROUTING --table nat --out-interface eth0 --jump MASQUERADE',
                'ip6tables --append POSTROUTING --table nat --out-interface eth0 --jump MASQUERADE'
            ]
            assert rule_list == exp_rule_list
