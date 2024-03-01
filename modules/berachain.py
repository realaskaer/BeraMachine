import random

from faker import Faker

from modules import RequestClient, Logger
from modules.interfaces import SoftwareException
from utils.tools import helper
from config import BEX_ABI, TOKENS_PER_CHAIN, BEX_CONTRACTS, ZERO_ADDRESS, HONEY_CONTRACTS, HONEY_ABI, HONEYJAR_ABI, \
    HONEYJAR_CONTRACTS, BEND_CONTRACTS, BEND_ABI, BERADOMAIN, BERADOMAIN_CONTRACTS, BERPS_CONTRACTS, BERPS_ABI


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
        self.honeyjar_contract2 = self.client.get_contract(HONEYJAR_CONTRACTS['bera_red'], HONEYJAR_ABI['router'])
        self.bend_contract = self.client.get_contract(BEND_CONTRACTS['router'], BEND_ABI['router'])
        self.berps_contract = self.client.get_contract(BERPS_CONTRACTS['router'], BERPS_ABI['router'])
        self.domain_contract = self.client.get_contract(BERADOMAIN_CONTRACTS['router'], BERADOMAIN['router'])

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
        amount = round(random.uniform(0.001, 0.003), 4)
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
    async def add_liquidity_bex_mim(self):
        amount = round(random.uniform(0.001, 0.003), 4)
        amount_in_wei = int(amount * 10 ** 18)

        self.logger_msg(*self.client.acc_info, msg=f'Add liquidity to BEX HONEY/MIM pool: {amount} HONEY')

        honey_token_address = TOKENS_PER_CHAIN['BeraChain']['HONEY']

        await self.client.check_for_approved(honey_token_address, BEX_CONTRACTS['router'], amount_in_wei)

        tx_params = await self.client.prepare_transaction(value=amount_in_wei)
        transaction = await self.bex_router_contract.functions.addLiquidity(
            BEX_CONTRACTS['bera_usdc_pool'],
            self.client.address,
            [honey_token_address],
            [amount_in_wei]
        ).build_transaction(tx_params)

        return await self.client.send_transaction(transaction)

    @helper
    async def swap_honey(self):

        amount = round(random.uniform(0.01, 0.05), 4)
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

    @helper
    async def mint_bera_red(self):

        self.logger_msg(*self.client.acc_info, msg=f'Mint BERA RED ENVELOPE. Price : 1.78 HONEY')

        from_token_address = TOKENS_PER_CHAIN[self.network]['HONEY']

        await self.client.check_for_approved(from_token_address, HONEYJAR_CONTRACTS['bera_red'], int(1.776 * 10 ** 18))

        transaction = await self.honeyjar_contract2.functions.buy().build_transaction(
            await self.client.prepare_transaction()
        )

        return await self.client.send_transaction(transaction)

    # @helper
    # async def mint_valhala_nft(self):
    #     url = 'https://mint.valhalla.land/site/character-mint-native-token'
    #
    #     payload = {
    #         'address': self.client.address
    #     }
    #
    #     headers = {
    #         "accept": "application/json, text/javascript, */*; q=0.01",
    #         "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    #         "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    #         "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Microsoft Edge\";v=\"122\"",
    #         "sec-ch-ua-mobile": "?0",
    #         "sec-ch-ua-platform": "\"Windows\"",
    #         "sec-fetch-dest": "empty",
    #         "sec-fetch-mode": "cors",
    #         'Cookie': 'advanced-frontend=hv3db91no3nmojqtlhrpdm34ia; _csrf=8efd9a44b9e5c088945e9fe00c244282a1e4fd3d85d5605260fb2e659e111b99a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22Wt66_45B74auzhKaY5rIcSTrapxxNqpB%22%3B%7D',
    #         "sec-fetch-site": "same-origin",
    #         "x-csrf-token": "pWcVT31UVrSdgD-2CRMbwBQ5lr8jidWqDLs4HPQjVe_yEyN5ImBj9qq0XsNze1ChTQzk9kDagdhty0BkulIlrQ==",
    #         "x-kl-saas-ajax-request": "Ajax_Request",
    #         "x-requested-with": "XMLHttpRequest",
    #         "referrer": "https://mint.valhalla.land/",
    #         "referrerPolicy": "strict-origin-when-cross-origin",
    #     }
    #
    #     response = await self.make_request(method="POST", url=url, headers=headers, data=f'wallet={self.client.address}')
    #
    #     print(response)
    #     return
    #
    #     self.logger_msg(*self.client.acc_info, msg=f'Mint BERA RED ENVELOPE. Price : 1.78 HONEY')
    #
    #     from_token_address = TOKENS_PER_CHAIN[self.network]['HONEY']
    #
    #     await self.client.check_for_approved(from_token_address, HONEYJAR_CONTRACTS['bera_red'], int(1.776 * 10 ** 18))
    #
    #     transaction = await self.honeyjar_contract2.functions.buy().build_transaction(
    #         await self.client.prepare_transaction()
    #     )
    #
    #     return await self.client.send_transaction(transaction)

    @helper
    async def supply_honey_bend(self):
        amount = round(random.uniform(0.01, 0.05), 4)
        amount_in_wei = int(amount * 10 ** 18)

        self.logger_msg(*self.client.acc_info, msg=f'Supply {amount} $HONEY on Bend Dashboard')

        from_token_address = TOKENS_PER_CHAIN[self.network]['HONEY']

        await self.client.check_for_approved(from_token_address, BEND_CONTRACTS['router'], amount_in_wei)

        transaction = await self.bend_contract.functions.supply(
            from_token_address,
            amount_in_wei,
            self.client.address,
            0
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def deposit_honey_berps_vault(self):
        amount = round(random.uniform(0.01, 0.05), 4)
        amount_in_wei = int(amount * 10 ** 18)

        self.logger_msg(*self.client.acc_info, msg=f'Staking {amount} $HONEY on Berps Vault')

        from_token_address = TOKENS_PER_CHAIN[self.network]['HONEY']

        await self.client.check_for_approved(from_token_address, BERPS_CONTRACTS['router'], amount_in_wei)

        transaction = await self.berps_contract.functions.deposit(
            amount_in_wei,
            self.client.address,
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def withdraw_honey_bend(self):
        self.logger_msg(*self.client.acc_info, msg=f'Withdraw $HONEY from Bend Dashboard')

        from_token_address = TOKENS_PER_CHAIN[self.network]['HONEY']

        transaction = await self.bend_contract.functions.withdraw(
            from_token_address,
            2 ** 256 - 1,
            self.client.address,
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def supply_btc_bend(self):
        amount = round(random.uniform(0.00001, 0.00005), 6)
        amount_in_wei = int(amount * 10 ** 18)

        self.logger_msg(*self.client.acc_info, msg=f'Supply {amount} $BTC on Bend Dashboard')

        from_token_address = TOKENS_PER_CHAIN[self.network]['WBTC']

        await self.client.check_for_approved(from_token_address, BEND_CONTRACTS['router'], amount_in_wei)

        transaction = await self.bend_contract.functions.supply(
            from_token_address,
            amount_in_wei,
            self.client.address,
            0
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def borrow_honey_bend(self):
        amount = round(random.uniform(0.01, 0.05), 4)
        amount_in_wei = int(amount * 10 ** 18)

        self.logger_msg(*self.client.acc_info, msg=f'Supply {amount} $HONEY on Bend Dashboard')

        from_token_address = TOKENS_PER_CHAIN[self.network]['HONEY']

        await self.client.check_for_approved(from_token_address, BEND_CONTRACTS['router'], amount_in_wei)

        transaction = await self.bend_contract.functions.supply(
            from_token_address,
            amount_in_wei,
            self.client.address,
            0
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def withdraw_btc_bend(self):
        self.logger_msg(*self.client.acc_info, msg=f'Withdraw $BTC from Bend Dashboard')

        from_token_address = TOKENS_PER_CHAIN[self.network]['WBTC']

        transaction = await self.bend_contract.functions.withdraw(
            from_token_address,
            2 ** 256 - 1,
            self.client.address,
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def supply_eth_bend(self):
        amount = round(random.uniform(0.00001, 0.0005), 6)
        amount_in_wei = int(amount * 10 ** 18)

        self.logger_msg(*self.client.acc_info, msg=f'Supply {amount} $ETH on Bend Dashboard')

        from_token_address = TOKENS_PER_CHAIN[self.network]['WETH']

        await self.client.check_for_approved(from_token_address, BEND_CONTRACTS['router'], amount_in_wei)

        transaction = await self.bend_contract.functions.supply(
            from_token_address,
            amount_in_wei,
            self.client.address,
            0
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def withdraw_eth_bend(self):
        self.logger_msg(*self.client.acc_info, msg=f'Withdraw $ETH from Bend Dashboard')

        from_token_address = TOKENS_PER_CHAIN[self.network]['WETH']

        transaction = await self.bend_contract.functions.withdraw(
            from_token_address,
            2 ** 256 - 1,
            self.client.address,
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transaction)

    @helper
    async def mint_domain(self):
        domain = f'{Faker().word()}{random.randint(100, 999)}'

        self.logger_msg(*self.client.acc_info, msg=f'Mint domain on BeraNames')

        self.logger_msg(*self.client.acc_info, msg=f'Generated domain: {domain}.🐻⛓️')

        transaction = await self.domain_contract.functions.mintNative(
            [str(i) for i in domain],
            1,
            self.client.address,
            'https://beranames.com/api/metadata/69',
            self.client.address,
        ).build_transaction(await self.client.prepare_transaction(value=360126764621146))

        return await self.client.send_transaction(transaction)
