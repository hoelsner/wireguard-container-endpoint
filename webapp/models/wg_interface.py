from typing import List


class WgInterfaceModel:
    """
    Wireguard Interface Data Model
    """
    intf_name: str
    description: str
    listen_port: int
    private_key: str
    endpoint: str
    cidr_address: List[str]

    table: str  # valid values off, auto

    @property
    def public_key(self):
        """compute public key from private key associated to the instance"""
        raise NotImplemented()
