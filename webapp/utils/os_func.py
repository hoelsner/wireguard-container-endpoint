"""
module that contains all os dependent functions which are normally mocked
as part of the unittests
"""
import ipaddress
import shlex
import subprocess
import logging
from typing import Tuple
from pyroute2 import IPRoute, NetlinkError


def run_subprocess(command: str, logger: logging.Logger) -> Tuple[str, str, bool]:
    """function to start a subprocess on the linux os, implemented to allow mocking with unit-tests

    :param command: _description_
    :type command: str
    :param logger: _description_
    :type logger: logging.Logger
    :return: stdout, stderr and success state
    :rtype: Tuple[str, str, bool]
    """
    success_state = True
    proc = subprocess.Popen(shlex.split(command), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=None)
    proc.wait()
    logger.debug(f"[{command!r} exited with {proc.returncode}]")

    if proc.returncode > 0:
        logger.error(f"unable to execute command '{command}': {proc.returncode}")
        success_state = False

    return stdout.decode(), stderr.decode(), success_state


def configure_route(intf_name: str, ip_network: str, operation: str, logger: logging.Logger) -> bool:
    """configure route on OS

    :param intf_name: _description_
    :type intf_name: str
    :param ip_network: _description_
    :type ip_network: str
    :param operation: "add" or "del"
    :type operation: str
    :return: True, if the route was altered as part of this call, False if not - will raise an Exception on error
    :rtype: bool
    """
    operation_performed = False
    if operation not in ["add", "del"]:
        raise AttributeError("operation must be add or del")

    # get data about the interface
    ip = IPRoute()
    intf_data_list = ip.link_lookup(ifname=intf_name)
    if len(intf_data_list) != 1:
        # interface not found, log error and return
        return

    dev = intf_data_list[0]

    # get friendly representation of routing table for check
    system_routes = ["{}/{}".format(dict(x['attrs'])['RTA_DST'], x["dst_len"]) for x in ip.get_routes() if "RTA_DST" in dict(x['attrs'])]
    logger.debug(f"got IP routes from system: {system_routes}")

    try:
        route_exists = False
        if ip_network.lower() in system_routes:
            route_exists = True

        if operation == "add" and route_exists:
            logger.debug(f"route {ip_network} already found in table, skip add call")

        elif operation == "del" and not route_exists:
            logger.debug(f"route {ip_network} not found in table, skip delete call")

        else:
            ip_network_clean = str(ipaddress.ip_interface(ip_network).network)
            response = ip.route(operation, dst=ip_network_clean, oif=dev)
            operation_performed = True
            logger.debug(f"route operation {operation} for '{ip_network_clean}' response: {response}")

    except NetlinkError as ex:
        # fails silent, because the input values are expected to be valid and there
        # must be an OS problem which breaks the application
        logger.error(f"failed to add route: {ex}")
        raise ex

    return operation_performed
