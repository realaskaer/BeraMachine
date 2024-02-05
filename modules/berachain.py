import random

from modules import RequestClient, Logger
from modules.interfaces import SoftwareException
from utils.tools import helper
from config import BEX_ABI, TOKENS_PER_CHAIN, BEX_CONTRACTS, ZERO_ADDRESS, HONEY_CONTRACTS, HONEY_ABI, HONEYJAR_ABI, \
    HONEYJAR_CONTRACTS


class BeraChain(Logger, RequestClient):
    def __init__(self, client):
        self.client = client
        Logger.__init__(self)
        RequestClient.__init__(self, client)

        self.network = self.client.network.name
        self.bex_router_contract = self.client.get_contract(BEX_CONTRACTS['router'], BEX_ABI['router'])
        self.honey_router_contract = self.client.get_contract(HONEY_CONTRACTS['router'], HONEY_ABI['router'])
        self.pool_contract = self.client.get_contract(BEX_CONTRACTS['bera_usdc_pool'], BEX_ABI['router'])
        self.honeyjar_contract = self.client.get_contract(HONEYJAR_CONTRACTS['router'], HONEYJAR_ABI['router'])

    async def get_min_amount_out(self, from_token_address: str, to_token_address: str, amount_in_wei: int):
        min_amount_out = await self.bex_router_contract.functions.querySwap(
            from_token_address,
            to_token_address,
            amount_in_wei
        ).call()

        return int(min_amount_out - (min_amount_out / 100 * 5))

    async def get_swap_steps(self, from_token_address: str, to_token_address: str, amount_in_wei: int):
        url = f'https://artio-80085-dex-router.berachain.com/dex/route'

        params = {
            'quoteAsset': to_token_address,
            'baseAsset': from_token_address,
            'amount': amount_in_wei,
            'swap_type': 'given_in',
        }

        return (await self.make_request(url=url, params=params))['steps']

    @helper
    async def swap_bex(self, swapdata:dict = None):

        from_token_name, to_token_name, amount, amount_in_wei = swapdata

        self.logger_msg(*self.client.acc_info, msg=f'Swap on BEX: {amount} {from_token_name} -> {to_token_name}')

        token_data = TOKENS_PER_CHAIN[self.network]

        native_address = token_data['BERA'].lower()
        from_token_address = token_data[from_token_name]
        to_token_address = token_data[to_token_name]
        swap_steps = await self.get_swap_steps(from_token_address, to_token_address, amount_in_wei)
        deadline = 99999999
        swap_data = []

        from_token_balance, _, _ = await self.client.get_token_balance(from_token_name, check_symbol=False)

        if from_token_balance >= amount_in_wei:

            if from_token_name != self.client.network.token:
                await self.client.check_for_approved(
                    from_token_address, BEX_CONTRACTS[self.network]['router'], amount_in_wei
                )

            for index, step in enumerate(swap_steps):
                swap_data.append([
                    self.client.w3.to_checksum_address(step["pool"]),
                    self.client.w3.to_checksum_address(step["assetIn"]) if step['assetIn'] != native_address else ZERO_ADDRESS,
                    int(step["amountIn"]),
                    self.client.w3.to_checksum_address(step["assetOut"]),
                    int(int(step["amountOut"]) * 0.95) if index != 0 else 0,
                    "0x"
                ])

            tx_params = await self.client.prepare_transaction(
                value=amount_in_wei if from_token_name == self.client.network.token else 0
            )

            transaction = await self.bex_router_contract.functions.batchSwap(
                0,
                swap_data,
                deadline
            ).build_transaction(tx_params)

            return await self.client.send_transaction(transaction)
        else:
            raise SoftwareException('Insufficient balance on account!')

    @helper
    async def add_liquidity_bex(self):
        amount = round(random.uniform(0.01, 0.03), 4)
        amount_in_wei = int(amount * 10 ** 18)

        self.logger_msg(*self.client.acc_info, msg=f'Add liquidity to BEX BERA/STGUSDC pool: {amount} BERA')

        tx_params = await self.client.prepare_transaction(value=amount_in_wei)
        transaction = await self.bex_router_contract.functions.addLiquidity(
            BEX_CONTRACTS['bera_usdc_pool'],
            self.client.address,
            [ZERO_ADDRESS],
            [amount_in_wei]
        ).build_transaction(tx_params)

        return await self.client.send_transaction(transaction)

    @helper
    async def swap_honey(self):

        amount = round(random.uniform(0.1, 0.5), 4)
        amount_in_wei = int(amount * 10 ** 18)

        self.logger_msg(*self.client.acc_info, msg=f'Swap on Honey: {amount} STGUSDC -> HONEY')

        from_token_address = TOKENS_PER_CHAIN[self.network]['STGUSDC']

        await self.client.check_for_approved(from_token_address, HONEY_CONTRACTS['router'], amount_in_wei)

        transaction = await self.honey_router_contract.functions.mint(
            self.client.address,
            from_token_address,
            amount_in_wei
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def mint_booga_ticket(self):

        self.logger_msg(*self.client.acc_info, msg=f'Mint NFT on 0xHONEYJAR. Price : 4.2 HONEY')

        from_token_address = TOKENS_PER_CHAIN[self.network]['HONEY']

        await self.client.check_for_approved(from_token_address, HONEYJAR_CONTRACTS['router'], int(4.2 * 10 ** 18))

        transaction = await self.honeyjar_contract.functions.buy().build_transaction(
            await self.client.prepare_transaction()
        )

        return await self.client.send_transaction(transaction)


    