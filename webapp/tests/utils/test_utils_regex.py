"""
Test Regex Utils
"""
# pylint: disable=missing-function-docstring
import re

import pytest

import utils.regex


def test_ipv4_address_regex():
    valid_entries = [
        "10.1.1.1",
        "172.43.232.12",
        "192.168.32.123",
        "2.3.4.5",
        "0.0.0.0",
        "255.255.255.255",
    ]
    invalid_entries = [
        "500.1.1.1",
        "a.231.23.2",
        "2..."
    ]

    pattern = re.compile(utils.regex.IPV4_ADDRESS_REGEX)
    for valid_entry in valid_entries:
        assert pattern.match(valid_entry) is not None, valid_entry

    for invalid_entry in invalid_entries:
        assert pattern.match(invalid_entry) is None, invalid_entry


def test_ipv4_interface_regex():
    valid_entries = [
        "10.1.1.1/32",
        "172.43.232.12/21",
        "192.168.32.123/32",
        "0.0.0.0/0",
        "2.3.4.5/8",
        "0.0.0.0/10",
        "255.255.255.255/32",
    ]
    invalid_entries = [
        "2.3.4.5/33",
        "0.0.0.0/a",
        "255.255.255.255/",
    ]

    pattern = re.compile(utils.regex.IPV4_INTERFACE_REGEX)
    for valid_entry in valid_entries:
        assert pattern.match(valid_entry) is not None, valid_entry

    for invalid_entry in invalid_entries:
        assert pattern.match(invalid_entry) is None, invalid_entry



def test_ipv6_address_regex():
    valid_entries = [
        "2000::1",
        "FD00::",
        "FD00::321"
    ]
    invalid_entries = [
        "FD0K::",
        "FD00:12312:321"
    ]

    pattern = re.compile(utils.regex.IPV6_ADDRESS_REGEX)
    for valid_entry in valid_entries:
        assert pattern.match(valid_entry) is not None, valid_entry

    for invalid_entry in invalid_entries:
        assert pattern.match(invalid_entry) is None, invalid_entry


def test_ipv6_interface_regex():
    valid_entries = [
        "FD00:0:0:0:0:0:0:321/123",
        "2000::/8",
        "FD00::/64",
        "FD00::321/123"
    ]
    invalid_entries = [
        "2000::/129",
        "FD00::/1111",
    ]

    pattern = re.compile(utils.regex.IPV6_INTERFACE_REGEX)
    for valid_entry in valid_entries:
        assert pattern.match(valid_entry) is not None, valid_entry

    for invalid_entry in invalid_entries:
        assert pattern.match(invalid_entry) is None, invalid_entry


def test_ipv4_or_ipv6_interface_regex():
    valid_entries = [
        "FD00:0:0:0:0:0:0:321/123",
        "2000::/8",
        "FD00::/64",
        "FD00::321/123",
        "10.1.1.1/32",
        "172.43.232.12/21",
        "192.168.32.123/32",
        "0.0.0.0/0",
        "2.3.4.5/8",
        "0.0.0.0/10",
        "255.255.255.255/32",
    ]
    invalid_entries = [
        "2000::/129",
        "FD00::/1111",
        "2.3.4.5/33",
        "0.0.0.0/a",
        "255.255.255.255/",
    ]

    pattern = re.compile(utils.regex.IPV4_OR_IPV6_INTERFACE_REGEX)
    for valid_entry in valid_entries:
        assert pattern.match(valid_entry) is not None, valid_entry

    for invalid_entry in invalid_entries:
        assert pattern.match(invalid_entry) is None, invalid_entry


def test_ipv4_or_ipv6_interface_csv_list_regex():
    valid_entries = [
        "FD00:0:0:0:0:0:0:321/123,FD00::/64,0.0.0.0/10",
        "2000::/8,2000::/8,2.3.4.5/8",
        "FD00::/64",
        "0.0.0.0/10",
        "255.255.255.255/32",
    ]
    invalid_entries = [
        "FD00:0:0:45678:0:0:0:321/123,FG00::/64,0.0.0.0/10",
        "2000:45678:/8,2000::/8, 2.3.4.5/8",
        "FD00:FREAK:/64",
        "0.0.0.999/10",
        "255.255.255.256/32",
    ]

    pattern = re.compile(utils.regex.IPV4_OR_IPV6_INTERFACE_CSV_LIST_REGEX)
    for valid_entry in valid_entries:
        assert pattern.match(valid_entry) is not None, valid_entry

    for invalid_entry in invalid_entries:
        assert pattern.match(invalid_entry) is None, invalid_entry


def test_wg_key_regex():
    valid_entries = [
        "cFWqYCq2NUwUE4hq6l6mvXN9sDiIvxg1pBudO+iZTnI=",
        "SDhQAzQY7njk6o48/YKpoqKLlijnjMgRdVKN2ixTgFY=",
    ]
    invalid_entries = [
        "cFWqYCq2NUwUE4hq6l6.vXN9sDiIvxg1pBudO+iZTnI=",
    ]

    pattern = re.compile(utils.regex.WG_KEY_REGEX)
    for valid_entry in valid_entries:
        assert pattern.match(valid_entry) is not None, valid_entry

    for invalid_entry in invalid_entries:
        assert pattern.match(invalid_entry) is None, invalid_entry
