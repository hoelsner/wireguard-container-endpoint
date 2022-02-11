"""
Custom validators for tortoise
"""
import re
from typing import Any, Union
import ipaddress
from tortoise.validators import Validator
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


class CustomRegexValidator(Validator):
    """
    A regex validator that proper handles null values
    """

    def __init__(self, pattern: str, flags: Union[int, re.RegexFlag]):
        self.regex = re.compile(pattern, flags)
        self.pattern = pattern

    def __call__(self, value: Any):
        if value is None:
            raise ValidationError(f"Value '{value}' does not match regex '{self.regex.pattern}'")

        if not self.regex.match(value):
            raise ValidationError(f"Value '{value}' does not match regex '{self.regex.pattern}'")
