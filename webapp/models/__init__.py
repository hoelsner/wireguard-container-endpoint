"""
data models for the application
"""
from models.wg_interface import WgInterfaceModel
from models.peer import WgPeerModel
from models.rules import AbstractIpTableRuleModel, Ipv4FilterRuleModel, Ipv4NatInterfaceRuleModel, FilterProtocolEnum, IpTableActionEnum, IpTableNameEnum
