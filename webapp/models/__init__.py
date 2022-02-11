"""
data models for the application
"""
from models.wg_interface import WgInterfaceModel, WgInterfaceTableEnum
from models.peer import WgPeerModel
from models.rules import AbstractIpTableRuleModel, Ipv4FilterRuleModel, Ipv4NatRuleModel, \
        FilterProtocolEnum, IpTableActionEnum, IpTableNameEnum, Ipv6FilterRuleModel, Ipv6NatRuleModel, \
        PolicyRuleListModel
