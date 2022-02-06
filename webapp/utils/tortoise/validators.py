"""
Custom validators for tortoise
"""
import ipaddress
from tortoise.exceptions import ValidationError


def validate_ipv4_network(value: str):
    """
    Validates that the given value is a valid IPv4 network address

    :raises ValidationError: if value is invalid
    """

    try:
        ipaddress.IPv4Network(value)

    except ValueError:
        raise ValidationError(f"'{value}' is not a valid IPv4 address.")


def validate_ipv6_network(value: str):
    """
    Validates that the given value is a valid IPv6 network address

    :raises ValidationError: if value is invalid
    """
    try:
        ipaddress.IPv6Network(value)

    except ValueError:
        raise ValidationError(f"'{value}' is not a valid IPv6 address.")
