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


async def swap_eth_bex(account_number, private_key, proxy, *_, **kwargs):
    worker = Custom(get_client(account_number, private_key, proxy))
    return await worker.swap_eth_bex(**kwargs)


async def swap_honey_bex(account_number, private_key, proxy, *_, **kwargs):
    worker = Custom(get_client(account_number, private_key, proxy))
    return await worker.swap_honey_bex(**kwargs)


async def swap_stgusdc_bex(account_number, private_key, proxy, *_, **kwargs):
    worker = Custom(get_client(account_number, private_key, proxy))
    return await worker.swap_stgusdc_bex(**kwargs)


async def add_liqiudity_bex_bera_usdc(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.add_liquidity_bex(**kwargs)


async def add_liqiudity_bex_honey_mim(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.add_liquidity_bex_mim(**kwargs)


async def supply_honey_bend(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.supply_honey_bend(**kwargs)


async def deposit_honey_berps(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.deposit_honey_berps_vault(**kwargs)


async def claim_bgt_on_berps(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.claim_bgt_on_berps(**kwargs)


async def delegate_bgt_on_station(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.delegate_bgt_on_station(**kwargs)


async def vote_bgt_on_station(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.vote_bgt_on_station(**kwargs)


async def deploy_contract(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.deploy_contract(**kwargs)


async def supply_btc_bend(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.supply_btc_bend(**kwargs)


async def supply_eth_bend(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.supply_eth_bend(**kwargs)


async def withdraw_honey_bend(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.withdraw_honey_bend(**kwargs)


async def withdraw_btc_bend(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.withdraw_btc_bend(**kwargs)


async def withdraw_eth_bend(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.withdraw_eth_bend(**kwargs)


async def mint_honey(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.swap_honey(**kwargs)


async def mint_booga_ticket(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.mint_booga_ticket(**kwargs)


async def mint_bera_red(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.mint_bera_red(**kwargs)


async def mint_valhala_nft(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.mint_valhala_nft(**kwargs)


async def mint_domain(account_number, private_key, proxy, *_, **kwargs):
    worker = BeraChain(get_client(account_number, private_key, proxy))
    return await worker.mint_domain(**kwargs)


async def claim_galxe_points(account_number, private_key, proxy, email_address, email_password, **kwargs):
    worker = Galxe(get_client(account_number, private_key, proxy, email_address, email_password))
    return await worker.claim_galxe_points_berachain_faucet(**kwargs)


async def claim_galxe_campaign_points(account_number, private_key, proxy, email_address, email_password, **kwargs):
    worker = Galxe(get_client(account_number, private_key, proxy, email_address, email_password))
    return await worker.claim_bera_campaign_points()
