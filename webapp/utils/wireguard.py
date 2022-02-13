"""
shared utilities for wireguard
"""
import wgconfig.wgexec

import utils.generics


class WgKeyUtilsException(Exception):
    """Exception for the WgKeyUtils"""
    pass


class WgKeyUtils(metaclass=utils.generics.SingletonMeta):
    """wireguard keys utility
    """
    def generate_private_key(self) -> str:
        """generate a new private key

        :return: [description]
        :rtype: str
        """
        try:
            return wgconfig.wgexec.generate_privatekey()

        except Exception as ex:
            raise WgKeyUtilsException("Unknown Exception") from ex

    def generate_preshared_key(self) -> str:
        """generate a new preshared key

        :return: [description]
        :rtype: str
        """
        try:
            return wgconfig.wgexec.generate_presharedkey()

        except Exception as ex:
            raise WgKeyUtilsException("Unknown Exception") from ex

    def get_public_key(self,private_key: str) -> str:
        """get the public key for a given private key

        :param private_key: [description]
        :type private_key: str
        :return: [description]
        :rtype: str
        """
        try:
            public_key = wgconfig.wgexec.get_publickey(private_key)

        except Exception as ex:
            raise WgKeyUtilsException("Unknown Exception") from ex

        if public_key is None:
            raise WgKeyUtilsException("cannot convert given public to private key")

        return public_key
