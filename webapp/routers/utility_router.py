"""
FastAPI router for common utilities
"""
import fastapi
import utils.wireguard


utility_router = fastapi.APIRouter()


@utility_router.post("/wg/generate/privkey")
def generate_privkey():
    """return a new private key
    """
    return {
        "private_key": utils.wireguard.WgKeyUtils().generate_private_key()
    }


@utility_router.post("/wg/generate/presharedkey")
def generate_presharedkey():
    """generate a new preshared key
    """
    return {
        "preshared_key": utils.wireguard.WgKeyUtils().generate_preshared_key()
    }
