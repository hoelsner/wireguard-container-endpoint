"""
module that contains all os dependent functions which are normally mocked
as part of the unittests
"""
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
    :return: _description_
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


def configure_route(intf_name: str, ip_network: str, operation: str, logger: logging.Logger):
    """configure route on OS

    :param intf_name: _description_
    :type intf_name: str
    :param ip_network: _description_
    :type ip_network: str
    :param operation: "add" or "del"
    :type operation: str
    """
    if operation not in ["add", "del"]:
        raise AttributeError("operation must be add or del")

    # get data about the interface
    ip = IPRoute()
    intf_data_list = ip.link_lookup(ifname=intf_name)
    if len(intf_data_list) != 1:
        # interface not found, log error and return
        return

    dev = intf_data_list[0]

    # add ip route, fails silently, because the input values are expected to be valid
    try:
        # TODO: add state check for route in OS
        response = ip.route(operation, dst=ip_network, oif=dev)
        logger.debug(f"route operation {operation} response: {response}")

    except NetlinkError as ex:
        logger.error(f"failed to add route: {ex}")
        raise ex
