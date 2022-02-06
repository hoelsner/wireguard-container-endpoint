from typing import List


class WgPeerModel:
    """
    Wireguard Peer Data Model
    """
    public_key: str
    friendly_name: str
    description: str
    persistent_keepalives: int      # optional
    preshared_key: str              # optional
    cidr_routes: List[str]

    @property
    def public_key_base64(self):
        """
        return a base 64 representation of the public key from the peer
        """
        raise NotImplemented()