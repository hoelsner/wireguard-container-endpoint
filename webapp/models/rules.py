"""
model classes, enums and exceptions for the rules and policy list of the application
"""
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
from enum import Enum
import logging
from abc import abstractmethod
from typing import List
from uuid import uuid4
import tortoise.query_utils
import tortoise.fields
import tortoise.models
import tortoise.validators
import utils.tortoise.validators
from utils.log import LoggingUtil


class FilterProtocolEnum(str, Enum):
    TCP = "tcp"
    UDP = "udp"


class IpTableActionEnum(str, Enum):
    DROP = "DROP"
    ACCEPT = "ACCEPT"


class IpTableNameEnum(str, Enum):
    INPUT = "INPUT"
    FORWARD = "FORWARD"


class PolicyRuleListModel(tortoise.models.Model):
    """
    Policy Rule List
    """
    instance_id = tortoise.fields.UUIDField(pk=True)
    name: str = tortoise.fields.CharField(
        max_length=32,
        null=False
    )
    ipv4_filter_rules: tortoise.fields.ReverseRelation["Ipv4FilterRuleModel"]
    ipv6_filter_rules: tortoise.fields.ReverseRelation["Ipv6FilterRuleModel"]
    ipv4_nat_rules: tortoise.fields.ReverseRelation["Ipv4NatRuleModel"]
    ipv6_nat_rules: tortoise.fields.ReverseRelation["Ipv6NatRuleModel"]

    async def to_ipv4_iptables_list(self, intf_name: str="%i", drop_rule: bool=False) -> List[str]:
        """convert ipv4 elements from policy to list of string values containing the iptable commands

        :param intf_name: name of the interface that should be used for the rule which represents the interface in the wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: convert iptable statement to remove the rule instead of add, defaults to False
        :type drop_rule: bool, optional
        :return: list of iptables commands
        :rtype: str
        """
        iptable_rules = list()

        await self.fetch_related(
            "ipv4_filter_rules",
            "ipv4_nat_rules",
        )

        for rule in self.ipv4_filter_rules:
            iptable_rules.append(rule.to_iptables_rule(intf_name=intf_name, drop_rule=drop_rule))

        for rule in self.ipv4_nat_rules:
            iptable_rules.append(rule.to_iptables_rule(intf_name=intf_name, drop_rule=drop_rule))

        return iptable_rules

    async def to_ipv6_iptables_list(self, intf_name: str="%i", drop_rule: bool=False) -> List[str]:
        """convert ipv6 elements from policy to list of string values containing the iptable commands

        :param intf_name: name of the interface that should be used for the rule which represents the interface in the wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: convert iptable statement to remove the rule instead of add, defaults to False
        :type drop_rule: bool, optional
        :return: list of iptables commands
        :rtype: str
        """
        iptable_rules = list()

        await self.fetch_related(
            "ipv6_filter_rules",
            "ipv6_nat_rules",
        )

        for rule in self.ipv6_filter_rules:
            iptable_rules.append(rule.to_iptables_rule(intf_name=intf_name, drop_rule=drop_rule))

        for rule in self.ipv6_nat_rules:
            iptable_rules.append(rule.to_iptables_rule(intf_name=intf_name, drop_rule=drop_rule))

        return iptable_rules

    async def to_iptables_list(self, intf_name: str="%i", drop_rule: bool=False) -> List[str]:
        """convert policy to list of string values containing the iptable commands

        :param intf_name: name of the interface that should be used for the rule which represents the interface in the wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: convert iptable statement to remove the rule instead of add, defaults to False
        :type drop_rule: bool, optional
        :return: list of iptables commands
        :rtype: str
        """
        iptable_rules = list()

        await self.fetch_related(
            "ipv4_filter_rules",
            "ipv6_filter_rules",
            "ipv4_nat_rules",
            "ipv6_nat_rules"
        )

        for rule in self.ipv4_filter_rules:
            iptable_rules.append(rule.to_iptables_rule(intf_name=intf_name, drop_rule=drop_rule))

        for rule in self.ipv6_filter_rules:
            iptable_rules.append(rule.to_iptables_rule(intf_name=intf_name, drop_rule=drop_rule))

        for rule in self.ipv4_nat_rules:
            iptable_rules.append(rule.to_iptables_rule(intf_name=intf_name, drop_rule=drop_rule))

        for rule in self.ipv6_nat_rules:
            iptable_rules.append(rule.to_iptables_rule(intf_name=intf_name, drop_rule=drop_rule))

        return iptable_rules

    class Meta:
        table = "policy_rule_list"


class AbstractIpTableRuleModel(tortoise.models.Model):
    """
    base class for iptable rules
    """
    instance_id = tortoise.fields.UUIDField(pk=True, default=uuid4)
    _logger: logging.Logger = LoggingUtil().logger

    def _to_iptables_rule(
        self,
        action: str,
        table: str,
        base_command: str = "iptable",
        intf_name: str=None,
        drop_rule: bool=False,
        src_network: str=None,
        dst_network: str=None,
        except_src: bool=False,
        except_dst: bool=False,
        protocol: str=None,
        dst_port_number: int=None,
        outgoing_intf_name: str=None
    ) -> str:
        """utility to generate iptables commands

        :param action: ACCEPT, DROP or MASQUERADE
        :type action: str
        :param table: target table for the rule
        :type table: str
        :param base_command: iptables base command, defaults to "iptable"
        :type base_command: str, optional
        :param intf_name: name of the interface that should be used for the rule which represents the interface in
                          wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: if true, the resulting rule will be used to remove the rule from the chain, defaults to False
        :type drop_rule: bool, optional
        :param src_net: source network if required, defaults to None
        :type src_net: str, optional
        :param dst_net: destination network if required, defaults to None
        :type dst_net: str, optional
        :param except_src: swap to except rule for source, defaults to False
        :type except_src: bool, optional
        :param except_dst: swap to except rule for destination, defaults to False
        :type except_dst: bool, optional
        :param protocol: protocol for port number if required (tcp/udp), defaults to None
        :type protocol: str, optional
        :param dst_port_number: destination port number if it should be filtered, defaults to None
        :type dst_port_number: int, optional
        :param outgoing_intf_name: outgoing interface name
        :type outgoing_intf_name: str, optional
        :return: iptables command string
        :rtype: str
        """
        operation = "-D" if drop_rule else "-A"
        table_statement = f"{table}" if action != "MASQUERADE" else f"{table} -t nat"
        base_rule = f"{base_command} {operation} {table_statement}"

        rule_intf_name = ""
        if intf_name:
            rule_intf_name = f" -i {intf_name}"

        rule_src = ""
        if src_network:
            rule_src = f" -s {src_network}" if not except_src else f" ! -s {src_network}"

        rule_dst = ""
        if dst_network:
            rule_dst = f" -d {dst_network}" if not except_dst else f" ! -d {dst_network}"

        rule_protocol = "" if not protocol else f" -p {protocol}"
        rule_dport = "" if not dst_port_number else f" -dport {dst_port_number}"

        rule_outgoing_intf_name = ""
        if outgoing_intf_name:
            rule_outgoing_intf_name = f" -o {outgoing_intf_name}"

        result_rule = f"{base_rule} {rule_intf_name}{rule_protocol}{rule_dport}{rule_src}{rule_dst}{rule_outgoing_intf_name} -j {action}".replace("  ", " ")

        # the following expression results in an invalid iptable and should result in an invalid rule
        result_rule_optional = f"{base_rule} {rule_intf_name} -j {action}".replace("  ", " ")
        if result_rule_optional == result_rule:
            # return an empty string, if the rule equals the result_rule which is then not a valid iptables statement
            self._logger.debug(f"RULE {repr(self)} IS IGNORED")
            return ""

        self._logger.debug(f"RULE {repr(self)} CONVERTED TO {result_rule}")
        return result_rule

    @abstractmethod
    def to_iptables_rule(self, intf_name: str="%i", drop_rule: bool=False) -> str:
        """get the rule as iptables statement

        :param intf_name: name of the interface that should be used for the rule which represents the interface in the wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: convert iptable statement to remove the rule instead of add, defaults to False
        :type drop_rule: bool, optional
        :return: iptable command representation of the model
        :rtype: str
        """
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    class Meta:
        abstract = True


class Ipv4FilterRuleModel(AbstractIpTableRuleModel):
    """
    Model for a IPv4 Filter Rule
    """
    policy_rule_list = tortoise.fields.ForeignKeyField(
        "models.PolicyRuleListModel",
        related_name="ipv4_filter_rules",
        null=True,
        on_delete=tortoise.fields.CASCADE
    )
    src_network = tortoise.fields.CharField(
        max_length=64,
        null=False,
        default="0.0.0.0/0",
        validators=[utils.tortoise.validators.validate_ipv4_network]
    )
    dst_network = tortoise.fields.CharField(
        max_length=64,
        null=False,
        default="0.0.0.0/0",
        validators=[utils.tortoise.validators.validate_ipv4_network]
    )
    # except_* - swap the *_address to "all except" within iptables
    except_src = tortoise.fields.BooleanField(default=False)
    except_dst = tortoise.fields.BooleanField(default=False)
    protocol = tortoise.fields.CharEnumField(
        enum_type=FilterProtocolEnum,
        max_length=8,
        null=True
    )
    action = tortoise.fields.CharEnumField(
        enum_type=IpTableActionEnum,
        max_length=8,
        null=False,
        # default to DROP rules, blacklist approach within app
        default=IpTableActionEnum.DROP
    )
    table = tortoise.fields.CharEnumField(
        enum_type=IpTableNameEnum,
        max_length=8,
        null=False,
        # default to routed traffic, focus on limiting the VPN peers
        default=IpTableNameEnum.FORWARD
    )
    dst_port_number = tortoise.fields.IntField(
        null=True,
        validators=[
            tortoise.validators.MinValueValidator(1),
            tortoise.validators.MaxValueValidator(65535)
        ]
    )

    def to_iptables_rule(self, intf_name: str="%i", drop_rule: bool=False) -> str:
        """get IPv4 rule as iptables statement

        :param intf_name: name of the interface that should be used for the rule which represents the interface in
                          wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: if true, the resulting rule will be used to remove the rule from the chain, defaults to False
        :type drop_rule: bool, optional
        :return: iptables command based on the content of the instance
        :rtype: str
        """
        return self._to_iptables_rule(
            action=self.action,
            table=self.table,
            base_command="iptable",
            intf_name=intf_name,
            drop_rule=drop_rule,
            # omit statement if entire IP space is affected
            src_network=self.src_network if self.src_network != "0.0.0.0/0" else None,
            dst_network=self.dst_network if self.dst_network != "0.0.0.0/0" else None,
            except_src=self.except_src,
            except_dst=self.except_dst,
            protocol=self.protocol,
            dst_port_number=self.dst_port_number
        )

    def __str__(self):
        return self.to_iptables_rule()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.pk} {self.src_network} {self.dst_network} {self.protocol} {self.dst_port_number} {self.action} {self.table}>"

    class Meta:
        table = "ipv4_filter_rules"

    class PydanticMeta:
        exclude = (
            "policy_rule_list.ipv4_filter_rules",
            "policy_rule_list.ipv6_filter_rules",
            "policy_rule_list.ipv4_nat_rules",
            "policy_rule_list.ipv6_nat_rules",
            "policy_rule_list.bound_interfaces"
        )


class Ipv6FilterRuleModel(AbstractIpTableRuleModel):
    """
    Model for a IPv6 Filter Rule
    """
    policy_rule_list = tortoise.fields.ForeignKeyField(
        "models.PolicyRuleListModel",
        related_name="ipv6_filter_rules",
        null=True,
        on_delete=tortoise.fields.CASCADE
    )
    src_network = tortoise.fields.CharField(
        max_length=64,
        null=False,
        default="::/0",
        validators=[utils.tortoise.validators.validate_ipv6_network]
    )
    dst_network = tortoise.fields.CharField(
        max_length=64,
        null=False,
        default="::/0",
        validators=[utils.tortoise.validators.validate_ipv6_network]
    )
    # except_* - swap the *_address to "all except" within iptables
    except_src = tortoise.fields.BooleanField(default=False)
    except_dst = tortoise.fields.BooleanField(default=False)
    protocol = tortoise.fields.CharEnumField(
        enum_type=FilterProtocolEnum,
        max_length=8,
        null=True
    )
    action = tortoise.fields.CharEnumField(
        enum_type=IpTableActionEnum,
        max_length=8,
        null=False,
        default=IpTableActionEnum.DROP
    )
    table = tortoise.fields.CharEnumField(
        enum_type=IpTableNameEnum,
        max_length=8,
        null=False,
        default=IpTableNameEnum.FORWARD
    )
    dst_port_number = tortoise.fields.IntField(
        null=True,
        validators=[
            tortoise.validators.MinValueValidator(1),
            tortoise.validators.MaxValueValidator(65535)
        ]
    )

    def to_iptables_rule(self, intf_name: str="%i", drop_rule: bool=False) -> str:
        """get IPv6 rule as iptables statement

        :param intf_name: name of the interface that should be used for the rule which represents the interface in
                          wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: if true, the resulting rule will be used to remove the rule from the chain, defaults to False
        :type drop_rule: bool, optional
        :return: iptables command based on the content of the instance
        :rtype: str
        """
        return self._to_iptables_rule(
            action=self.action,
            table=self.table,
            base_command="ip6table",
            intf_name=intf_name,
            drop_rule=drop_rule,
            # omit statement if entire IP space is affected
            src_network=self.src_network if self.src_network != "::/0" else None,
            dst_network=self.dst_network if self.dst_network != "::/0" else None,
            except_src=self.except_src,
            except_dst=self.except_dst,
            protocol=self.protocol,
            dst_port_number=self.dst_port_number
        )

    def __str__(self):
        return self.to_iptables_rule()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.pk} {self.src_network} {self.dst_network} {self.protocol} {self.dst_port_number} {self.action} {self.table}>"

    class Meta:
        table = "ipv6_filter_rules"

    class PydanticMeta:
        exclude = (
            "policy_rule_list.ipv4_filter_rules",
            "policy_rule_list.ipv6_filter_rules",
            "policy_rule_list.ipv4_nat_rules",
            "policy_rule_list.ipv6_nat_rules",
            "policy_rule_list.bound_interfaces"
        )


class Ipv4NatRuleModel(AbstractIpTableRuleModel):
    """
    NAT rule for a defined interface (always POSTROUTING with MASQUERADE)
    """
    policy_rule_list = tortoise.fields.ForeignKeyField(
        "models.PolicyRuleListModel",
        related_name="ipv4_nat_rules",
        null=True,
        on_delete=tortoise.fields.CASCADE
    )
    target_interface: str = tortoise.fields.CharField(
        max_length=32,
        null=False,
        default="eth0"
    )

    def to_iptables_rule(self, intf_name: str="%i", drop_rule: bool=False) -> str:
        """get NAT rule

        :param intf_name: name of the interface that should be used for the rule which represents the interface in
                          wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: if true, the resulting rule will be used to remove the rule from the chain, defaults to False
        :type drop_rule: bool, optional
        :return: iptables command based on the content of the instance
        :rtype: str
        """
        if intf_name != "%i":
            self._logger.warning("attribute intf_name changed on NAT rule, but attribute is ignored")

        return self._to_iptables_rule(
            base_command="iptable",
            drop_rule=drop_rule,
            table="POSTROUTING",
            action="MASQUERADE",
            outgoing_intf_name=self.target_interface
        )

    def __str__(self):
        return self.to_iptables_rule()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.instance_id}>"

    class Meta:
        table = "ipv4_nat_rules"

    class PydanticMeta:
        exclude = (
            "policy_rule_list.ipv4_filter_rules",
            "policy_rule_list.ipv6_filter_rules",
            "policy_rule_list.ipv4_nat_rules",
            "policy_rule_list.ipv6_nat_rules",
            "policy_rule_list.bound_interfaces"
        )


class Ipv6NatRuleModel(AbstractIpTableRuleModel):
    """
    NAT rule for a defined interface (always POSTROUTING with MASQUERADE)
    """
    policy_rule_list = tortoise.fields.ForeignKeyField(
        "models.PolicyRuleListModel",
        related_name="ipv6_nat_rules",
        null=True,
        on_delete=tortoise.fields.CASCADE
    )
    target_interface: str = tortoise.fields.CharField(
        max_length=32,
        null=False,
        default="eth0"
    )

    def to_iptables_rule(self, intf_name: str="%i", drop_rule: bool=False) -> str:
        """get NAT rule

        :param intf_name: name of the interface that should be used for the rule which represents the interface in
                          wireguard configuration, defaults to "%i"
        :type intf_name: str, optional
        :param drop_rule: if true, the resulting rule will be used to remove the rule from the chain, defaults to False
        :type drop_rule: bool, optional
        :return: iptables command based on the content of the instance
        :rtype: str
        """
        if intf_name != "%i":
            self._logger.warning("attribute intf_name changesd on NAT rule, but attribute is ignored")

        return self._to_iptables_rule(
            base_command="ip6table",
            drop_rule=drop_rule,
            table="POSTROUTING",
            action="MASQUERADE",
            outgoing_intf_name=self.target_interface
        )

    def __str__(self):
        return self.to_iptables_rule()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.instance_id}>"

    class Meta:
        table = "ipv6_nat_rules"

    class PydanticMeta:
        exclude = (
            "policy_rule_list.ipv4_filter_rules",
            "policy_rule_list.ipv6_filter_rules",
            "policy_rule_list.ipv4_nat_rules",
            "policy_rule_list.ipv6_nat_rules",
            "policy_rule_list.bound_interfaces"
        )
