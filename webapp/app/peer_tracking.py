"""
Peer tracking module
"""
import logging

from fastapi_utils.tasks import repeat_every

import models
import utils.config
import utils.generics
import utils.wireguard


@repeat_every(
    seconds=utils.config.ConfigUtil().peer_tracking_timer,
    wait_first=True
)
async def run_peer_tracking() -> None:
    """update ip routing table based on the
    """
    logger = logging.getLogger("peer_tracking")
    logger.debug("run peer tracking...")

    ip_adapter = utils.wireguard.IpRouteAdapter()
    for entry in await models.WgPeerModel.all():
        # create ip route entries if not exists
        await entry.fetch_related("wg_interface")
        if await entry.is_active():
            for ip_net in entry.cidr_routes_list:
                ip_adapter.add_ip_route(intf_name=entry.wg_interface.intf_name, ip_network=ip_net)
        else:
            for ip_net in entry.cidr_routes_list:
                ip_adapter.remove_ip_route(intf_name=entry.wg_interface.intf_name, ip_network=ip_net)
