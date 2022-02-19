# pylint: disable=missing-function-docstring
import pytest

import wgconfig.wgexec
import utils.wireguard


def broken_function(*args, **kwargs) -> str:
    raise Exception("An Exception")


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
    def test_read_function(self):
        """test basic read function for the operational state
        """
        # TODO: implement test cases for TestWgSystemInfoAdapter
        pytest.skip("implement test case")
