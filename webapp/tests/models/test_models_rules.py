"""
test rules models
"""
# pylint: disable=unused-argument
import pytest
from fastapi.testclient import TestClient

import models


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpv4FilterRuleModel:
    """
    Test Ipv4FilterRuleModel model
    """
    async def test_rule_with_port(self, test_client: TestClient, clean_db):
        """test rule with port filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            protocol=models.FilterProtocolEnum.TCP,
            dst_port_number=3000
        )

        exp_rule = "iptables --append FORWARD --in-interface %i --protocol tcp --dport 3000 --jump DROP"
        assert frm.to_iptables_rule() == exp_rule
        assert frm.__str__() == exp_rule

        exp_rule = "iptables --append FORWARD --in-interface eth0 --protocol tcp --dport 3000 --jump DROP"
        assert frm.to_iptables_rule(intf_name="eth0") == exp_rule

        exp_rule = "iptables --delete FORWARD --in-interface %i --protocol tcp --dport 3000 --jump DROP"
        assert frm.to_iptables_rule(drop_rule=True) == exp_rule

    async def test_rule_with_ip_addresses(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24"
        )

        exp_rule = "iptables --append FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP"
        assert frm.to_iptables_rule() == exp_rule

    async def test_ignore_rule(self, test_client: TestClient, clean_db):
        """test empty rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl
        )

        assert frm.to_iptables_rule() == ""

    async def test_rule_with_ip_addresses_and_action(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter with action
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            action=models.IpTableActionEnum.ACCEPT
        )

        exp_rule = "iptables --append FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump ACCEPT"
        assert frm.to_iptables_rule() == exp_rule

    async def test_rule_with_ip_addresses_and_table(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter with table
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            table=models.IpTableNameEnum.INPUT
        )

        exp_rule = "iptables --append INPUT --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP"
        assert frm.to_iptables_rule() == exp_rule

    async def test_rule_with_ip_addresses_and_except(self, test_client: TestClient, clean_db):
        """test rule with except IPv4 network filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            except_src=True,
            except_dst=True
        )

        exp_rule = "iptables --append FORWARD --in-interface %i ! --source 192.168.1.0/24 ! --destination 192.168.2.0/24 --jump DROP"
        assert frm.to_iptables_rule() == exp_rule


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpv6FilterRuleModel:
    """
    Test Ipv6FilterRuleModel model
    """
    async def test_rule_with_ip_addresses(self, test_client: TestClient, clean_db):
        """test rule with IPv4 network filter
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv6FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="2001:DB8:0::/64",
            dst_network="2001:DB8:1::/64"
        )

        exp_rule = "ip6tables --append FORWARD --in-interface %i --source 2001:DB8:0::/64 --destination 2001:DB8:1::/64 --jump DROP"
        assert frm.to_iptables_rule() == exp_rule
        assert frm.__str__() == exp_rule

        # fetch through API
        response = await test_client.get("/api/rules/filters/ipv6")
        assert response.status_code == 200, response.text

        data = response.json()
        assert len(data) == 1
        assert data[0]["instance_id"] == str(frm.instance_id), response.text


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpv4NatRuleModel:
    """
    Test TestIpv4NatRuleModel model
    """
    async def test_nat_rule_output(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4NatRuleModel.create(
            policy_rule_list=prl
        )

        exp_rule = "iptables --append POSTROUTING --table nat --out-interface eth0 --jump MASQUERADE"
        assert frm.to_iptables_rule() == exp_rule
        assert frm.__str__() == exp_rule

    async def test_nat_rule_output_with_interface_name(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv4NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth8"
        )

        exp_rule = "iptables --append POSTROUTING --table nat --out-interface eth8 --jump MASQUERADE"
        assert frm.to_iptables_rule(intf_name="foo") == exp_rule, "This must not change anything on the iptables command"
        assert frm.__str__() == exp_rule


@pytest.mark.usefixtures("disable_os_level_commands")
class TestIpv6NatRuleModel:
    """
    Test TestIpv6NatRuleModel model
    """
    async def test_nat_rule_output(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv6NatRuleModel.create(
            policy_rule_list=prl
        )

        exp_rule = "ip6tables --append POSTROUTING --table nat --out-interface eth0 --jump MASQUERADE"
        assert frm.to_iptables_rule() == exp_rule
        assert frm.__str__() == exp_rule

    async def test_nat_rule_output_with_interface_name(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")
        frm = await models.Ipv6NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth8"
        )

        exp_rule = "ip6tables --append POSTROUTING --table nat --out-interface eth8 --jump MASQUERADE"
        assert frm.to_iptables_rule(intf_name="foo") == exp_rule, "This must not change anything on the iptables command"
        assert frm.__str__() == exp_rule


@pytest.mark.usefixtures("disable_os_level_commands")
class TestPolicyRuleListModel:
    """
    Test PolicyRuleList model
    """
    async def _create_test_data(self, prl: models.PolicyRuleListModel):
        """create test data for the class"""
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            protocol=models.FilterProtocolEnum.TCP,
            dst_port_number=3000
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24"
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            action=models.IpTableActionEnum.ACCEPT
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            table=models.IpTableNameEnum.INPUT
        )
        await models.Ipv4FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="192.168.1.0/24",
            dst_network="192.168.2.0/24",
            except_src=True,
            except_dst=True
        )
        await models.Ipv6FilterRuleModel.create(
            policy_rule_list=prl,
            src_network="2001:DB8:0::/64",
            dst_network="2001:DB8:1::/64"
        )
        await models.Ipv4NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth1"
        )
        await models.Ipv6NatRuleModel.create(
            policy_rule_list=prl,
            target_interface="eth8"
        )

    async def test_basics(self, test_client: TestClient, clean_db):
        """test the generation of a NAT rule
        """
        prl = await models.PolicyRuleListModel.create(name="foo")

        amount = await models.PolicyRuleListModel.all()
        assert len(amount) == 1

    async def test_iptable_rule_list(self, test_client: TestClient, clean_db):
        """test full iptable rule list
        """
        prl = await models.PolicyRuleListModel.create(name="test_policy")
        await self._create_test_data(prl)

        expected_create_result = [
            "iptables --append FORWARD --in-interface %i --protocol tcp --dport 3000 --jump DROP",
            "iptables --append FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP",
            "iptables --append FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump ACCEPT",
            "iptables --append INPUT --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP",
            "iptables --append FORWARD --in-interface %i ! --source 192.168.1.0/24 ! --destination 192.168.2.0/24 --jump DROP",
            "ip6tables --append FORWARD --in-interface %i --source 2001:DB8:0::/64 --destination 2001:DB8:1::/64 --jump DROP",
            "iptables --append POSTROUTING --table nat --out-interface eth1 --jump MASQUERADE",
            "ip6tables --append POSTROUTING --table nat --out-interface eth8 --jump MASQUERADE"
        ]
        expected_drop_result = [
            "iptables --delete FORWARD --in-interface %i --protocol tcp --dport 3000 --jump DROP",
            "iptables --delete FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP",
            "iptables --delete FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump ACCEPT",
            "iptables --delete INPUT --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP",
            "iptables --delete FORWARD --in-interface %i ! --source 192.168.1.0/24 ! --destination 192.168.2.0/24 --jump DROP",
            "ip6tables --delete FORWARD --in-interface %i --source 2001:DB8:0::/64 --destination 2001:DB8:1::/64 --jump DROP",
            "iptables --delete POSTROUTING --table nat --out-interface eth1 --jump MASQUERADE",
            "ip6tables --delete POSTROUTING --table nat --out-interface eth8 --jump MASQUERADE"
        ]

        result = await prl.to_iptables_list(intf_name="%i", drop_rule=False)
        assert expected_create_result == result

        result = await prl.to_iptables_list(intf_name="%i", drop_rule=True)
        assert expected_drop_result == result

    async def test_ipv4_iptable_rule_list(self, test_client: TestClient, clean_db):
        """test ipv4 iptable rule list
        """
        prl = await models.PolicyRuleListModel.create(name="test_policy")
        await self._create_test_data(prl)

        expected_create_result_ipv4 = [
            "iptables --append FORWARD --in-interface %i --protocol tcp --dport 3000 --jump DROP",
            "iptables --append FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP",
            "iptables --append FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump ACCEPT",
            "iptables --append INPUT --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP",
            "iptables --append FORWARD --in-interface %i ! --source 192.168.1.0/24 ! --destination 192.168.2.0/24 --jump DROP",
            "iptables --append POSTROUTING --table nat --out-interface eth1 --jump MASQUERADE"
        ]
        expected_drop_result_ipv4 = [
            "iptables --delete FORWARD --in-interface %i --protocol tcp --dport 3000 --jump DROP",
            "iptables --delete FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP",
            "iptables --delete FORWARD --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump ACCEPT",
            "iptables --delete INPUT --in-interface %i --source 192.168.1.0/24 --destination 192.168.2.0/24 --jump DROP",
            "iptables --delete FORWARD --in-interface %i ! --source 192.168.1.0/24 ! --destination 192.168.2.0/24 --jump DROP",
            "iptables --delete POSTROUTING --table nat --out-interface eth1 --jump MASQUERADE"
        ]
        result = await prl.to_ipv4_iptables_list(intf_name="%i", drop_rule=False)
        assert expected_create_result_ipv4 == result

        result = await prl.to_ipv4_iptables_list(intf_name="%i", drop_rule=True)
        assert expected_drop_result_ipv4 == result

    async def test_ipv6_iptable_rule_list(self, test_client: TestClient, clean_db):
        """test ipv6 iptable rule list
        """
        prl = await models.PolicyRuleListModel.create(name="test_policy")
        await self._create_test_data(prl)

        expected_create_result_ipv6 = [
            "ip6tables --append FORWARD --in-interface %i --source 2001:DB8:0::/64 --destination 2001:DB8:1::/64 --jump DROP",
            "ip6tables --append POSTROUTING --table nat --out-interface eth8 --jump MASQUERADE"
        ]
        expected_drop_result_ipv6 = [
            "ip6tables --delete FORWARD --in-interface %i --source 2001:DB8:0::/64 --destination 2001:DB8:1::/64 --jump DROP",
            "ip6tables --delete POSTROUTING --table nat --out-interface eth8 --jump MASQUERADE"
        ]
        result = await prl.to_ipv6_iptables_list(intf_name="%i", drop_rule=False)
        assert expected_create_result_ipv6 == result

        result = await prl.to_ipv6_iptables_list(intf_name="%i", drop_rule=True)
        assert expected_drop_result_ipv6 == result
