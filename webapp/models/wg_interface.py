"""
model classes for the wireguard interface
"""
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
import re
from enum import Enum
from typing import List, Optional, Type

import tortoise.fields
import tortoise.models
import tortoise.validators
import tortoise.signals
import wgconfig.wgexec

import app.wg_config_adapter
import utils.regex
import utils.log
import utils.tortoise.validators
import models.rules
import models.peer


class WgInterfaceTableEnum(str, Enum):
    """Enum for the table configuration value
    """
    OFF = "off"
    AUTO = "auto"


class WgInterfaceModel(tortoise.models.Model):
    """
    Wireguard Interface Data Model
    """
    instance_id = tortoise.fields.UUIDField(pk=True)
    intf_name: str = tortoise.fields.CharField(
        max_length=32,
        null=False,
        unique=True,
        validators=[
            # interface naming convention according https://man7.org/linux/man-pages/man8/wg-quick.8.html
            tortoise.validators.RegexValidator("^[a-zA-Z0-9_=+.-]{1,15}$", re.I)
        ],
        description="wireguard interface name"
    )
    policy_rule_list: models.rules.PolicyRuleListModel = tortoise.fields.ForeignKeyField(
        "models.PolicyRuleListModel",
        related_name="bound_interfaces",
        null=True,
        on_delete=tortoise.fields.SET_NULL,
        description="associated interface policy"
    )
    description: str = tortoise.fields.CharField(
        max_length=2048,
        default="",
        null=True,
        validators=[
            utils.tortoise.validators.RegexOrNoneValidator("^[a-zA-Z0-9_]*$", re.I)
        ],
        description="description within the wireguard configuration"
    )
    listen_port: int = tortoise.fields.IntField(
        default=51820,
        unique=True,
        validators=[
            tortoise.validators.MinValueValidator(1),
            tortoise.validators.MaxValueValidator(65535)
        ],
        description="port number that should be used"
    )
    private_key: str = tortoise.fields.CharField(
        max_length=64,
        null=False,
        validators=[
            tortoise.validators.RegexValidator(utils.regex.WG_KEY_REGEX, re.I)
        ],
        description="private key of the interface"
    )
    table: str = tortoise.fields.CharEnumField(
        enum_type=WgInterfaceTableEnum,
        max_length=8,
        default=WgInterfaceTableEnum.AUTO
    )
    cidr_addresses: str = tortoise.fields.CharField(
        max_length=2048,
        null=False,
        validators=[
            utils.tortoise.validators.CustomRegexValidator(utils.regex.IPV4_OR_IPV6_INTERFACE_CSV_LIST_REGEX, re.I)
        ],
        description="comma separated list of IPv4/IPv6 addresses that are used on the wireguard interface"
    )
    peers: tortoise.fields.ReverseRelation["WgPeerModel"]

    @property
    def cidr_addresses_list(self) -> List:
        """return CIDR addresses as list

        :return: [description]
        :rtype: List
        """
        return [x.strip() for x in self.cidr_addresses.split(",")]

    @cidr_addresses_list.setter
    def cidr_addresses_list(self, value: list) -> None:
        """[summary]

        :param ipv46_list: [description]
        :type ipv46_list: list
        """
        self.cidr_addresses = ", ".join(value)

    @property
    def public_key(self) -> str:
        """compute public key from private key associated to the instance

        :raises NotImplementedError: [description]
        :return: [description]
        :rtype: str
        """
        return wgconfig.wgexec.get_publickey(self.private_key)

    class Meta:
        table = "wg_interfaces"


@tortoise.signals.post_save(WgInterfaceModel)
async def wginterfacemodel_pre_save(
    sender: "Type[WgInterfaceModel]",
    instance: WgInterfaceModel,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    """trigger sync with wgconfig"""
    logger = utils.log.LoggingUtil().logger

    logger.info(f"update interface config '{instance.intf_name}'")
    adapter = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)

    # (re-)initialize configuration for wireguard configuration
    await adapter.init_config(force_overwrite=True)
    await adapter.rebuild_peer_config()
    await adapter.apply_config(recreate_interface=True)

@tortoise.signals.post_delete(WgInterfaceModel)
async def wginterfacemodel_pre_delete(
    sender: "Type[WgInterfaceModel]",
    instance: WgInterfaceModel,
    using_db: "Optional[BaseDBAsyncClient]"
) -> None:
    """trigger sync with wgconfig"""
    logger = utils.log.LoggingUtil().logger

    logger.info(f"remove interface '{instance.intf_name}'")
    await app.wg_config_adapter.WgConfigAdapter(wg_interface=instance).interface_down()
