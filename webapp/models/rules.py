"""
model classes, enums and exceptions for the rules and policy list of the application
"""
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
from enum import Enum
import logging
from abc import abstractmethod
from typing import List
import tortoise.fields
import tortoise.models
import tortoise.validators
import utils
import utils.tortoise.validators


class FilterProtocolEnum(str, Enum):
    TCP = "tcp"
    UDP = "udp"


class IpTableActionEnum(str, Enum):
    DROP = "DROP"
    ACCEPT = "ACCEPT"


class IpTableNameEnum(str, Enum):
    INPUT = "INPUT"
    FORWARD = "FORWARD"


class InvalidIpv4Rule(Exception):
    """Exception thrown if the update of an property will lead to an invalid IPv4 rule"""
    pass


class InvalidIpv6Rule(Exception):
    """Exception thrown if the update of an property will lead to an invalid IPv6 rule"""
    pass


class AbstractIpTableRuleModel(tortoise.models.Model):
    """
    base class for iptable rules
    """
    instance_id = tortoise.fields.UUIDField(pk=True)
    _iptable_base_command = "iptable"
    _logger: logging.Logger = utils.LoggingUtil().logger

    @abstractmethod
    def to_iptables_rule(self, intf_name: str="%i", drop_rule: bool=False) -> str:
        """
        get the rule as iptables statement

        :param intf_name: name of the interface that should be used for the rule, defaults to %i which represents the
        interface in wireguard configuration
        :param drop_rule: if true, the resulting rule will be used to remove the rule from the chain
        :raises InvalidIpv4Rule:
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
    _iptable_base_command = "iptable"

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
        """
        get IPv4 rule as iptables statement

        :param intf_name: name of the interface that should be used for the rule, defaults to %i which represents the interface in wireguard configuration
        :param drop_rule: if true, the resulting rule will be used to remove the rule from the chain
        :raises InvalidIpv4Rule: thrown if the rule is not a valid IPv4 filter rule
        """
        operation = "-D" if drop_rule else "-A"
        base_rule = f"{self._iptable_base_command} {operation} {self.table} -i {intf_name}"

        rule_src = "" if self.src_network == "0.0.0.0/0" else f" -s {self.src_network}" if self.except_src else f"! -s {self.src_network}"
        rule_dst = "" if self.dst_network == "0.0.0.0/0" else f" -s {self.dst_network}" if self.except_dst else f"! -d {self.dst_network}"
        rule_protocol = "" if not self.protocol else f" -p {self.protocol}"
        rule_dport = "" if not self.dst_port_number else f" -dport {self.dst_port_number}"

        result_rule = f"{base_rule} {rule_protocol}{rule_dport}{rule_src}{rule_dst} -j {self.action}".replace("  ", " ")
        if base_rule == result_rule:
            # return an empty string, if the rule equals the result_rule which is then not a valid iptables statement
            self._logger.debug(f"RULE {repr(self)} IS IGNORED")
            return ""

        self._logger.debug(f"RULE {repr(self)} CONVERTED TO {result_rule}")
        return result_rule

    def __str__(self):
        return self.to_iptables_rule()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.pk} {self.src_network} {self.dst_network} {self.protocol} {self.dst_port_number} {self.action} {self.table}>"

    class Meta:
        table = "ipv4_filter_rules"


class Ipv4NatInterfaceRuleModel(AbstractIpTableRuleModel):
    """
    NAT rule for a defined interface (always POSTROUTING with MASQUERADE)
    """
    _iptable_base_command = "iptable"
    target_interface: str = "eth0"

    def to_iptables_rule(self, intf_name: str="%i", drop_rule: bool=False) -> str:
        """
        get IPv4 rule as iptables statement
        :param intf_name: name of the interface that should be used for the rule, defaults to %i which represents the interface in wireguard configuration
        :param drop_rule: if true, the resulting rule will be used to remove the rule from the chain
        :raises InvalidIpv4Rule:
        """
        raise NotImplementedError()

    def __str__(self):
        return self.to_iptables_rule()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    class Meta:
        table = "ipv4_nat_rules"


class PolicyRuleList:
    """
    Policy Rule List
    """
    _policy_rules: List[AbstractIpTableRuleModel]

    def __iter__(self):
        for e in self._policy_rules:
            yield e

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self._policy_rules)

    def __len__(self):
        return len(self._policy_rules)

    def __getitem__(self, ii):
        return self._policy_rules[ii]

    def __delitem__(self, ii):
        del self._policy_rules[ii]

    def __setitem__(self, ii, val):
        if isinstance(val, AbstractIpTableRuleModel):
            self._policy_rules[ii] = val

        raise AttributeError("List item must be an instance of AbstractIpTableRule")

    def __str__(self):
        return str(self._policy_rules)

    class Meta:
        table = "policy_rule_list"
