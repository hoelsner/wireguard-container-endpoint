"""
Regular Expressions that are used within the application
"""

_IPV4_ADDRESS_REGEX = r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
IPV4_ADDRESS_REGEX = rf"^{_IPV4_ADDRESS_REGEX}$"
_IPV4_INTERFACE_REGEX = rf"({_IPV4_ADDRESS_REGEX})\/((3[0-2])|([12][0-9])|([0-9]))"
IPV4_INTERFACE_REGEX = rf"^{_IPV4_INTERFACE_REGEX}$"

_IPV6_ADDRESS_REGEX = r"(?:(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}|(?=(?:[A-F0-9]{0,4}:){0,7}[A-F0-9]{0,4}(?![:.\w]))(([0-9A-F]{1,4}:){1,7}|:)((:[0-9A-F]{1,4}){1,7}|:)|(?:[A-F0-9]{1,4}:){7}:|:(:[A-F0-9]{1,4}){7})(?![:.\w])"
IPV6_ADDRESS_REGEX = rf"^{_IPV6_ADDRESS_REGEX}$"
_IPV6_INTERFACE_REGEX = rf"{_IPV6_ADDRESS_REGEX}\/(\d{{1,2}}|1[0-1]\d|12[0-8])"
IPV6_INTERFACE_REGEX = rf"^{_IPV6_INTERFACE_REGEX}$"

_IPV4_OR_IPV6_INTERFACE_REGEX = rf"(({_IPV4_INTERFACE_REGEX})|({_IPV6_INTERFACE_REGEX}))"
IPV4_OR_IPV6_INTERFACE_REGEX = rf"^{_IPV4_OR_IPV6_INTERFACE_REGEX}$"

IPV4_OR_IPV6_INTERFACE_CSV_LIST_REGEX = rf"^({_IPV4_OR_IPV6_INTERFACE_REGEX})(,\s*{_IPV4_OR_IPV6_INTERFACE_REGEX})*$"

WG_KEY_REGEX = "^[A-Za-z0-9+\/]{42}[A|E|I|M|Q|U|Y|c|g|k|o|s|w|4|8|0]=$"
