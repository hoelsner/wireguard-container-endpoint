# pylint: disable=missing-class-docstring
import re
from typing import List, Optional, Type

import tortoise.fields
import tortoise.validators
import tortoise.models
from tortoise import BaseDBAsyncClient

import app.wg
import utils.regex
import utils.tortoise.validators


class WgPeerModel(tortoise.models.Model):
    """
    Wireguard Peer Data Model
    """
    instance_id = tortoise.fields.UUIDField(pk=True)
    wg_interface = tortoise.fields.ForeignKeyField(
        "models.WgInterfaceModel",
        related_name="peers",
        on_delete=tortoise.fields.CASCADE
    )
    public_key = tortoise.fields.CharField(
        max_length=64,
        null=False,
        validators=[
            tortoise.validators.RegexValidator(utils.regex.WG_KEY_REGEX, re.I)
        ],
        description="public key of the peer"
    )
    friendly_name = tortoise.fields.CharField(
        max_length=64,
        null=True,
        validators=[
            utils.tortoise.validators.RegexOrNoneValidator(utils.regex.WG_KEY_REGEX, re.I)
        ]
    )
    description = tortoise.fields.CharField(
        max_length=2048,
        default="",
        null=True
    )
    persistent_keepalives = tortoise.fields.IntField(
        null=True,
        default=-1
    )
    preshared_key = tortoise.fields.CharField(
        max_length=64,
        null=True,
        validators=[
            utils.tortoise.validators.RegexOrNoneValidator(utils.regex.WG_KEY_REGEX, re.I)
        ],
        description="optional preshared key"
    )
    endpoint = tortoise.fields.CharField(
        max_length=64,
        null=True,
        description="optional endpoint to connect to the service"
    )
    cidr_routes = tortoise.fields.CharField(
        max_length=2048,
        null=False,
        validators=[
            utils.tortoise.validators.CustomRegexValidator(utils.regex.IPV4_OR_IPV6_INTERFACE_CSV_LIST_REGEX, re.I)
        ],
        description="comma separated list of IPv4/IPv6 for the client"
    )

    @property
    def cidr_routes_list(self) -> List:
        """return CIDR routes as list

        :return: [description]
        :rtype: List
        """
        return [x.strip() for x in self.cidr_routes.split(",")]

    @cidr_routes_list.setter
    def cidr_routes_list(self, value: list) -> None:
        """set CIDR route value based on list

        :param ipv46_list: [description]
        :type ipv46_list: list
        """
        self.cidr_routes = ", ".join(value)

    def __str__(self):
        if self.friendly_name:
            return "{} ({})".format(self.friendly_name, self.public_key)

        return self.public_key

    class Meta:
        table = "wg_peers"


@tortoise.signals.post_save(WgPeerModel)
async def wgpeermodel_pre_save(
    sender: "Type[WgPeerModel]",
    instance: WgPeerModel,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    """trigger sync with wgconfig"""
    await instance.fetch_related("wg_interface")
    await app.wg.WgConfigAdapter(wg_interface=instance.wg_interface).update_peer_config()


@tortoise.signals.post_delete(WgPeerModel)
async def wgpeermodel_pre_delete(
    sender: "Type[WgPeerModel]",
    instance: WgPeerModel,
    using_db: "Optional[BaseDBAsyncClient]"
) -> None:
    """trigger sync with wgconfig"""
    await instance.fetch_related("wg_interface")
    await app.wg.WgConfigAdapter(wg_interface=instance.wg_interface).update_peer_config()
