from tortoise.transactions import in_transaction

import models
import utils.log
import utils.config


async def run() -> bool:
    """run initial configuration
    """
    config_util = utils.config.ConfigUtil()
    init_config = utils.config.InitConfigUtil()
    logger = utils.log.LoggingUtil().logger

    if init_config.has_init_config():
        wg_interface = await models.WgInterfaceModel.get_or_none(intf_name=init_config.intf_name)
        if wg_interface is None:
            logger.debug("create wireguard interface...")
            try:
                async with in_transaction() as t:
                    prl = await models.PolicyRuleListModel.create(
                        name=init_config.policy_name
                    )

                    # create NAT rule
                    if init_config.policy_nat_enable:
                        logger.debug("create NAT rules...")
                        await models.Ipv4NatRuleModel.create(
                            policy_rule_list=prl,
                            target_interface=init_config.policy_nat_intf
                        )
                        await models.Ipv6NatRuleModel.create(
                            policy_rule_list=prl,
                            target_interface=init_config.policy_nat_intf
                        )

                    # create allow/deny admin rule
                    if not init_config.policy_allow_admin:
                        logger.debug("create Filter rules...")
                        await models.Ipv4FilterRuleModel.create(
                            policy_rule_list=prl,
                            protocol=models.FilterProtocolEnum.TCP,
                            action=models.IpTableActionEnum.DROP,
                            dst_port_number=config_util.api_port,
                            table=models.IpTableNameEnum.INPUT
                        )
                        await models.Ipv6FilterRuleModel.create(
                            policy_rule_list=prl,
                            protocol=models.FilterProtocolEnum.TCP,
                            action=models.IpTableActionEnum.DROP,
                            dst_port_number=config_util.api_port,
                            table=models.IpTableNameEnum.INPUT
                        )

                    # create wireguard interface
                    wg_intf = await models.WgInterfaceModel.create(
                        intf_name=init_config.intf_name,
                        policy_rule_list=prl,
                        description="interface created by initial configuration wizard",
                        listen_port=init_config.intf_listen_port,
                        private_key=init_config.intf_private_key,
                        cidr_addresses=init_config.intf_cidr_addresses
                    )

                    # create public key
                    await models.WgPeerModel.create(
                        wg_interface=wg_intf,
                        public_key=init_config.peer_public_key,
                        friendly_name="initial peer",
                        description="peer created as initial interface",
                        persistent_keepalives=init_config.peer_persistent_keepalive,
                        preshared_key=init_config.peer_preshared_key,
                        endpoint=init_config.peer_endpoint,
                        cidr_routes=init_config.peer_cidr_routes
                    )

            except Exception as ex:
                logger.fatal(f"UNABLE TO APPLY INITIAL DATA\n\n{ex}\n\n")
                return False

    return True