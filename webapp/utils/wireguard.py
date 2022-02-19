"""
shared utilities for wireguard
"""
import json
import logging

import wgconfig.wgexec

import utils.generics
import utils.os_func
import utils.config


class WgSystemInfoException(Exception):
    """exception thrown if something is wrong within the WgSystemInfoAdapter class"""
    pass


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


class WgSystemInfoAdapter(utils.generics.AsyncSubProcessMixin, metaclass=utils.generics.SingletonMeta):
    """
    read operational data for wireguard
    """
    def __init__(self):
        self._logger = logging.getLogger("wg_sysinfo")

    async def get_wg_json(self) -> dict:
        """get raw response from the wireguard operational data

        :return: dict of wireguard
        :rtype: dict
        """
        result = None
        stdout, stderr, success = await self._execute_subprocess("wg-json")
        if not success:
            raise WgSystemInfoException("unable to run wg-json: {stderr}")

        try:
            result = json.loads(stdout.strip())

        except Exception as ex:
            raise WgSystemInfoException("unable to fetch operational data for wireguard") from ex

        return result


class IpRouteAdapter(metaclass=utils.generics.SingletonMeta):
    """
    System Level IP routing adapter to created and delete routes in the local routing table
    """
    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger("peer_tracking")
        self._config = utils.config.ConfigUtil()

    def add_ip_route(self, intf_name: str, ip_network: str):
        """add ip route to local routing table

        :param intf_name: [description]
        :type intf_name: str
        :param ip_network: [description]
        :type ip_network: str
        """
        self.logger.info(f"add route {ip_network} for interface {intf_name}")
        try:
            utils.os_func.configure_route(
                intf_name=intf_name,
                ip_network=ip_network,
                operation="add",
                logger=self.logger
            )

        except Exception:
            # just log the error and ignore it silently
            self.logger.error(f"unable to add route {ip_network} for {intf_name}", exc_info=self._config.debug)

    def remove_ip_route(self, intf_name: str, ip_network: str):
        """remove the route from the given routing table

        :param intf_name: [description]
        :type intf_name: str
        :param ip_network: [description]
        :type ip_network: str
        """
        self.logger.info(f"remove route {ip_network} for interface {intf_name}")
        try:
            utils.os_func.configure_route(
                intf_name=intf_name,
                ip_network=ip_network,
                operation="del",
                logger=self.logger
            )

        except Exception:
            # just log the error and ignore it silently
            self.logger.error(f"unable to add route {ip_network} for {intf_name}", exc_info=self._config.debug)
