import random

from faker import Faker

from modules import RequestClient, Logger
from modules.interfaces import SoftwareException
from utils.tools import helper
from config import BEX_ABI, TOKENS_PER_CHAIN, BEX_CONTRACTS, ZERO_ADDRESS, HONEY_CONTRACTS, HONEY_ABI, HONEYJAR_ABI, \
    HONEYJAR_CONTRACTS, BEND_CONTRACTS, BEND_ABI, BERADOMAIN_ABI, BERADOMAIN_CONTRACTS, BERPS_CONTRACTS, BERPS_ABI, \
    STATION_CONTRACTS, STATION_ABI


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
        self.domain_contract = self.client.get_contract(BERADOMAIN_CONTRACTS['router'], BERADOMAIN_ABI['router'])
        self.station_contract = self.client.get_contract(STATION_CONTRACTS['delegate'], STATION_ABI['delegate'])
        self.station_contract2 = self.client.get_contract(STATION_CONTRACTS['vote'], STATION_ABI['vote'])

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
            BEX_CONTRACTS['bera_mim_pool'],
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
    async def claim_bgt_on_berps(self):
        amount_in_wei = int(await self.berps_contract.functions.pendingBGT(self.client.address).call() * 0.99)

        self.logger_msg(*self.client.acc_info, msg=f'Claim {amount_in_wei / 10 ** 18:.6f} $BGT on Berps Vault')

        transaction = await self.berps_contract.functions.claimBGT(
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

    @helper
    async def delegate_bgt_on_station(self):
        self.logger_msg(*self.client.acc_info, msg=f'Delegate $BGT BeraChain Station')

        bgt_contract = self.client.get_contract(TOKENS_PER_CHAIN[self.network]['BGT'])

        amount_in_wei = await bgt_contract.functions.balanceOf(self.client.address).call()

        delegate_list = [
            "0x032238ba76Aadaa7C891967c4491fC18f81C6189",
            "0x0331A9665E8f47b4C289eb665f8466f68e9ae9a5",
            "0x034855669054BEbe87374317F1c848237a591046",
            "0x041e8463219316724eFBBE827409ABD1a57D9F6e",
            "0x0484Cc87F35088af7a0bCe3b155FFE2e91A9baa8",
            "0x069da50b99408c8c42d006AfbF3C7F600384edEA",
            "0x06A7D20154c336be6103B2D588e6c6ECeB571186",
            "0x0cf633F3a7478EAAbd73B7287B997D609B12A11a",
            "0x1C6Da144428b409aCB125ad0c26291DA6D484411",
            "0x07c74a2fEDCfC793FbD3adc5C9f5f864Af297b96",
            "0x26de86e871eab1E471AEd9fe343D4d75800EB587",
            "0x1Cc335D9c67a71C777282fdb28b0a2d5eBf42AF4",
            "0x46d2305eaFd69E9323d13328f5915C1fcE287f2F",
            "0x75d57E65d4330772293De0D5C2dBcA8f16F1A74F",
            "0x6F259Fc8B8eFCED1971824F3723e8798936Fef76",
        ]

        transcation = await self.station_contract.functions.delegate(
            random.choice(delegate_list),
            amount_in_wei
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transcation)

    @helper
    async def vote_bgt_on_station(self):
        self.logger_msg(*self.client.acc_info, msg=f'Vote on BeraChain Station')

        transcation = await self.station_contract2.functions.vote(
            random.randint(70, 93),
            1,
            ''
        ).build_transaction(await self.client.prepare_transaction())

        return await self.client.send_transaction(transcation)

    @helper
    async def deploy_contract(self):

        self.logger_msg(*self.client.acc_info, msg=f'Deploy contract on BeraChain')

        contract_data = ('0x60806040526000805461ffff1916905534801561001b57600080fd5b5060fb8061002a6000396000f3fe60806'
                         '04052348015600f57600080fd5b506004361060325760003560e01c80630c55699c146037578063b49004e91460'
                         '5b575b600080fd5b60005460449061ffff1681565b60405161ffff909116815260200160405180910390f35b606'
                         '16063565b005b60008054600191908190607a90849061ffff166096565b92506101000a81548161ffff02191690'
                         '8361ffff160217905550565b61ffff81811683821601908082111560be57634e487b7160e01b6000526011600452'
                         '60246000fd5b509291505056fea2646970667358221220666c87ec501268817295a4ca1fc6e3859faf241f38dd68'
                         '8f145135970920009264736f6c63430008120033')

        transcation = await self.client.prepare_transaction() | {
            'data': contract_data
        }

        return await self.client.send_transaction(transcation)