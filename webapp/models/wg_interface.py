"""
model classes for the wireguard interface
"""
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
import re
from enum import Enum
from typing import List
import tortoise.fields
import tortoise.models
import tortoise.validators
import wgconfig.wgexec

import utils.regex
import utils.tortoise.validators


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
    policy_rule_list = tortoise.fields.ForeignKeyField(
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
