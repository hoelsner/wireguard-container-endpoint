# pylint: disable=missing-class-docstring,missing-function-docstring,unused-argument
import json
import time

import pytest
import wgconfig.wgexec

import utils.os_func
import utils.wireguard


def broken_function(*args, **kwargs) -> str:
    raise Exception("An Exception")

def mock_wg_json_command_invalid_format(command: str, **kwargs):
    return "I'm not JSON", "", True

def mock_wg_json_command_with_inactive_peer(command: str, **kwargs):
    data = {
        "wgvpn16": {
                "privateKey": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
                "publicKey": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
                "listenPort": 51820,
                "peers": {
                        "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=": {
                                "presharedKey": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
                                "endpoint": "172.29.0.1:62818",
                                "latestHandshake": int(time.time()) - (60*2+1),
                                "transferRx": 82224,
                                "transferTx": 1680,
                                "allowedIps": [
                                        "172.29.1.16/32",
                                        "fd00:1::16/128"
                                ]
                        }
                }
        }
    }
    return json.dumps(data, indent=4), "", True

def mock_wg_json_command(command: str, **kwargs):
    data = {
        "wgvpn16": {
                "privateKey": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
                "publicKey": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
                "listenPort": 51820,
                "peers": {
                        "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=": {
                                "presharedKey": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
                                "endpoint": "172.29.0.1:62818",
                                "latestHandshake": int(time.time()),
                                "transferRx": 82224,
                                "transferTx": 1680,
                                "allowedIps": [
                                        "172.29.1.16/32",
                                        "fd00:1::16/128"
                                ]
                        }
                }
        }
    }
    return json.dumps(data, indent=4), "", True


class TestWgKeyUtils:
    """test WgKeyUtils class"""
    def test_generate_private_key(self):
        key1 = utils.wireguard.WgKeyUtils().generate_private_key()
        key2 = utils.wireguard.WgKeyUtils().generate_private_key()

        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert key1 != key2

    def test_generate_private_key_with_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(wgconfig.wgexec, "generate_privatekey", broken_function)
            with pytest.raises(utils.wireguard.WgKeyUtilsException):
                utils.wireguard.WgKeyUtils().generate_private_key()

    def test_generate_preshared_key(self):
        key1 = utils.wireguard.WgKeyUtils().generate_preshared_key()
        key2 = utils.wireguard.WgKeyUtils().generate_preshared_key()

        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert key1 != key2

    def test_generate_preshared_key_with_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(wgconfig.wgexec, "generate_presharedkey", broken_function)
            with pytest.raises(utils.wireguard.WgKeyUtilsException):
                utils.wireguard.WgKeyUtils().generate_preshared_key()

    def test_get_public_key(self):
        priv_key = "MLwlAhfhTqPBH3ECxOY29X8DVox4rdOtrThomeUfG30="
        expected_pubkey = "MXyxRNdUXUYrfP/mzDGMor0uCuvcPMm2mxCAXDZ2v34="
        assert expected_pubkey == utils.wireguard.WgKeyUtils().get_public_key(priv_key)

        with pytest.raises(utils.wireguard.WgKeyUtilsException) as ex:
            utils.wireguard.WgKeyUtils().get_public_key("invalid")

        assert ex.match("cannot convert given public to private key")

    def test_get_public_key_with_exception(self, monkeypatch):
        with monkeypatch.context() as m:
            m.setattr(wgconfig.wgexec, "get_publickey", broken_function)
            with pytest.raises(utils.wireguard.WgKeyUtilsException):
                utils.wireguard.WgKeyUtils().get_public_key("MLwlAhfhTqPBH3ECxOY29X8DVox4rdOtrThomeUfG30=")


class TestWgSystemInfoAdapter:
    """
    Test WgSystemInfoAdapter utility
    """
    async def test_get_wg_json(self, monkeypatch):
        """test basic read function for the operational state
        """
        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command)

            wg_si_adapter = utils.wireguard.WgSystemInfoAdapter()
            op_data = await wg_si_adapter.get_wg_json()
            assert isinstance(op_data, dict)
            assert "wgvpn16" in op_data.keys()

    async def test_get_wg_json_with_error_command(self, monkeypatch):
        """test what happens if the read of the operational state failed if the command failed
        """
        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", broken_function)

            wg_si_adapter = utils.wireguard.WgSystemInfoAdapter()
            with pytest.raises(utils.wireguard.WgSystemInfoException) as ex:
                await wg_si_adapter.get_wg_json()

            assert ex.match("unable to fetch operational data for wireguard")

    async def test_get_wg_json_with_error_format(self, monkeypatch):
        """test what happens if the read of the operational state failed if the format is broken
        """
        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command_invalid_format)

            wg_si_adapter = utils.wireguard.WgSystemInfoAdapter()
            with pytest.raises(utils.wireguard.WgSystemInfoException) as ex:
                await wg_si_adapter.get_wg_json()

            assert ex.match("unable to fetch operational data for wireguard")

    async def test_is_peer_active_with_active_peer(self, monkeypatch):
        """test is_peer_active with active peers
        """
        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command)

            wg_si_adapter = utils.wireguard.WgSystemInfoAdapter()
            # peershould be, timestamp is current execution time
            assert await wg_si_adapter.is_peer_active(
                "wgvpn16",
                "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs="
            ) is True

    async def test_is_peer_active_with_inactive_peer(self, monkeypatch):
        """test is_peer_active with inactive peers
        """
        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command_with_inactive_peer)

            wg_si_adapter = utils.wireguard.WgSystemInfoAdapter()
            assert await wg_si_adapter.is_peer_active(
                "wgvpn16",
                "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs="
            ) is False, await wg_si_adapter.get_wg_json()

    async def test_is_peer_active_with_invalid_interface(self, monkeypatch):
        """test is_peer_active with missing interface (should fail with log message and return False)
        """
        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command)

            wg_si_adapter = utils.wireguard.WgSystemInfoAdapter()
            assert await wg_si_adapter.is_peer_active(
                "wgvpn11",
                "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs="
            ) is False

    async def test_is_peer_active_with_invalid_peer(self, monkeypatch):
        """test is_peer_active with missing peer (should fail with log message and return False)
        """
        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command)

            wg_si_adapter = utils.wireguard.WgSystemInfoAdapter()
            assert await wg_si_adapter.is_peer_active(
                "wgvpn16",
                "ImNotAValidPubkey"
            ) is False

    async def test_is_peer_active_with_broken_wg_conf(self, monkeypatch):
        """test is_peer_active with broken wg_conf command (should fail with log message and return False)
        """
        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command_invalid_format)

            wg_si_adapter = utils.wireguard.WgSystemInfoAdapter()
            assert await wg_si_adapter.is_peer_active(
                "wgvpn16",
                "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs="
            ) is False


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpRouteAdapter:
    def test_clean_ip_network(self):
        """test internal cleanup method for ip networks
        """
        test_data_set = {
            "10.1.1.1/24": "10.1.1.0/24",
            "FD00::1/64": "fd00::/64",
        }
        ipr_adapter = utils.wireguard.IpRouteAdapter()
        for test_value, expected_result in test_data_set.items():
            assert expected_result == ipr_adapter._clean_ip_network(test_value)

    def test_add_ip_route_performed(self, monkeypatch):
        """test add ip route performed
        """
        def configure_route_true_mock(**kwargs):
            return True

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "configure_route", configure_route_true_mock)

            ipr_adapter = utils.wireguard.IpRouteAdapter()
            assert ipr_adapter.add_ip_route("wg1", "10.1.1.1/24") is True

    def test_add_ip_route_already_exist(self, monkeypatch):
        """test add ip route existing
        """
        def configure_route_true_mock(**kwargs):
            return False

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "configure_route", configure_route_true_mock)

            ipr_adapter = utils.wireguard.IpRouteAdapter()
            assert ipr_adapter.add_ip_route("wg1", "10.1.1.1/24") is False

    def test_add_ip_route_failure(self, monkeypatch):
        """test add ip route failure
        """
        def configure_route_true_mock(**kwargs):
            raise Exception("An Exception")

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "configure_route", configure_route_true_mock)

            ipr_adapter = utils.wireguard.IpRouteAdapter()
            assert ipr_adapter.add_ip_route("wg1", "10.1.1.1/24") is False

    def test_remove_ip_route_performed(self, monkeypatch):
        """test remove ip route performed
        """
        def configure_route_true_mock(**kwargs):
            return True

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "configure_route", configure_route_true_mock)

            ipr_adapter = utils.wireguard.IpRouteAdapter()
            assert ipr_adapter.remove_ip_route("wg1", "10.1.1.1/24") is True

    def test_remove_ip_route_already_exist(self, monkeypatch):
        """test remove ip route existing
        """
        def configure_route_true_mock(**kwargs):
            return False

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "configure_route", configure_route_true_mock)

            ipr_adapter = utils.wireguard.IpRouteAdapter()
            assert ipr_adapter.remove_ip_route("wg1", "10.1.1.1/24") is False

    def test_remove_ip_route_failure(self, monkeypatch):
        """test remove ip route failure
        """
        def configure_route_true_mock(**kwargs):
            raise Exception("An Exception")

        with monkeypatch.context() as m:
            m.setattr(utils.os_func, "configure_route", configure_route_true_mock)

            ipr_adapter = utils.wireguard.IpRouteAdapter()
            assert ipr_adapter.remove_ip_route("wg1", "10.1.1.1/24") is False
