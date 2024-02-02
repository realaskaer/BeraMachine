from modules import *
from utils.networks import *


def get_client(account_number, private_key, proxy, email_address=None, email_password=None) -> Client:
    return Client(account_number, private_key, proxy, email_address, email_password)


def get_network_by_chain_id(chain_id):
    return {
        48: BeraChainRPC
    }[chain_id]


async def mint_berachain_tokens(account_number, private_key, proxy, *_):
    worker = Faucet(get_client(account_number, private_key, proxy))
    return await worker.claim_berachain_tokens()


async def swap_bex(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.swap_bex(**kwargs)


async def swap_btc_bex(account_number, private_key, proxy, *_, **kwargs):
    worker = Custom(get_client(account_number, private_key, proxy))
    return await worker.swap_btc_bex(**kwargs)


async def swap_stgusdc_bex(account_number, private_key, proxy, *_, **kwargs):
    worker = Custom(get_client(account_number, private_key, proxy))
    return await worker.swap_stgusdc_bex(**kwargs)


async def add_liqiudity_bex(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.add_liquidity_bex(**kwargs)


async def mint_honey(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.swap_honey(**kwargs)


async def claim_galxe_points(account_number, private_key, proxy, email_address, email_password, **kwargs):
    worker = Galxe(get_client(account_number, private_key, proxy, email_address, email_password))
    return await worker.claim_galxe_points_berachain_faucet(**kwargs)