"""
shared utilities for wireguard
"""
import json
import time
import ipaddress
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
    read operational data for wireguard and extend based on this one
    """
    # delta between the handshake and the current time before the peer is considered
    # inactive
    _time_delta_to_be_down = 60 * 2

    def __init__(self):
        self._logger = logging.getLogger("wg_sysinfo")

    async def is_peer_active(self, wg_interface_name: str, public_key: str) -> bool:
        """guess if the given peer is active on the given interface

        :param wg_interface_name: interface, where the client should be active
        :type wg_interface_name: str
        :param public_key: public key to look for
        :type public_key: str
        :return: _description_
        :rtype: bool
        """
        client_active = False
        try:
            op_data = await self.get_wg_json()
            if wg_interface_name in op_data.keys():
                peers_data = op_data[wg_interface_name]["peers"]
                if public_key in peers_data.keys():
                    peer_data = peers_data[public_key]
                    if "latestHandshake" in peer_data:
                        # if the peer handshake was within the last two minutes,
                        # the client seems to be active
                        time_delta = int(time.time()) - peer_data["latestHandshake"]
                        if self._time_delta_to_be_down >= time_delta:
                            self._logger.debug(f"peer '{public_key}' on interface '{wg_interface_name}' is considered ACTIVE (delta: {self._time_delta_to_be_down}>={time_delta})")
                            client_active = True

                        else:
                            self._logger.debug(f"peer '{public_key}' on interface '{wg_interface_name}' is considered INACTIVE (delta: {self._time_delta_to_be_down}>={time_delta})")

                    else:
                        self._logger.debug(f"latestHandshake not found for peer peer '{public_key}' on interface '{wg_interface_name}'")

                else:
                    self._logger.warning(f"peer '{public_key}' on interface '{wg_interface_name}' not found")

            else:
                self._logger.error(f"interface '{wg_interface_name}' not found in op state")

        except WgSystemInfoException:
            self._logger.fatal("unable to identify active state for peer '{public_key}' on interface '{wg_interface_name}' (invalid data)", exc_info=True)
            client_active = False

        except Exception:
            self._logger.fatal("unable to identify active state for peer '{public_key}' on interface '{wg_interface_name}' (unknown error)", exc_info=True)
            client_active = False

        return client_active

    async def get_wg_json(self) -> dict:
        """get raw response from the wireguard operational data

        :return: dict of wireguard
        :rtype: dict
        """
        result = None

        try:
            stdout, stderr, success = await self._execute_subprocess("wg-json")
            if not success:
                raise WgSystemInfoException("unable to run wg-json: {stderr}")

            result = json.loads(stdout.strip())

        except Exception as ex:
            raise WgSystemInfoException(f"unable to fetch operational data for wireguard ({ex})") from ex

        return result


class IpRouteAdapter(metaclass=utils.generics.SingletonMeta):
    """
    System Level IP routing adapter to created and delete routes in the local routing table
    """
    logger: logging.Logger

    def __init__(self):
        self.logger = logging.getLogger("peer_tracking")
        self._config = utils.config.ConfigUtil()

    def _clean_ip_network(self, ip_network) -> str:
        """clean ip_network parater

        :param value: _description_
        :type value: _type_
        :return: _description_
        :rtype: str
        """
        ip_network_clean = str(ipaddress.ip_interface(ip_network).network)
        return ip_network_clean.lower()

    def add_ip_route(self, intf_name: str, ip_network: str) -> bool:
        """add ip route to local routing table

        :param intf_name: [description]
        :type intf_name: str
        :param ip_network: [description]
        :type ip_network: str
        :return: True if performed, otherwise False
        :rtype: bool
        """
        operation_performed = False
        try:
            operation_performed = utils.os_func.configure_route(
                intf_name=intf_name,
                ip_network=self._clean_ip_network(ip_network),
                operation="add",
                logger=self.logger
            )
            if operation_performed:
                self.logger.info(f"route {ip_network} for interface {intf_name} added")

        except Exception:
            # just log the error and ignore it silently
            self.logger.error(f"unable to add route {ip_network} for {intf_name}", exc_info=self._config.debug)

        return operation_performed

    def remove_ip_route(self, intf_name: str, ip_network: str) -> bool:
        """remove the route from the given routing table

        :param intf_name: [description]
        :type intf_name: str
        :param ip_network: [description]
        :type ip_network: str
        :return: True if performed, otherwise False
        :rtype: bool
        """
        operation_performed = False
        try:
            operation_performed = utils.os_func.configure_route(
                intf_name=intf_name,
                ip_network=self._clean_ip_network(ip_network),
                operation="del",
                logger=self.logger
            )
            if operation_performed:
                self.logger.info(f"route {ip_network} for interface {intf_name} removed")

        except Exception:
            # just log the error and ignore it silently
            self.logger.error(f"unable to add route {ip_network} for {intf_name}", exc_info=self._config.debug)

        return operation_performed
