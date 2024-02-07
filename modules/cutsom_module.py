import random

from modules import Logger, RequestClient
from utils.tools import helper


class Custom(Logger, RequestClient):
    def __init__(self, client):
        self.client = client
        Logger.__init__(self)
        RequestClient.__init__(self, client)

    @helper
    async def swap_stgusdc_bex(self):
        from functions import swap_bex

        from_token_name = 'BERA'
        to_token_name = 'STGUSDC'
        amount = round(random.uniform(0.01, 0.03), 4)
        amount_in_wei = int(amount * 10 ** 18)

        data = from_token_name, to_token_name, amount, amount_in_wei

        result = await swap_bex(self.client.account_name, self.client.private_key,
                                self.client.proxy_init, swapdata=data)

        return result

    @helper
    async def swap_btc_bex(self):
        from functions import swap_bex

        from_token_name = 'BERA'
        to_token_name = 'WBTC'
        amount = round(random.uniform(0.01, 0.03), 4)
        amount_in_wei = int(amount * 10 ** 18)

        data = from_token_name, to_token_name, amount, amount_in_wei

        result = await swap_bex(self.client.account_name, self.client.private_key,
                                self.client.proxy_init, swapdata=data)

        return result

    @helper
    async def swap_honey_bex(self):
        from functions import swap_bex

        from_token_name = 'BERA'
        to_token_name = 'HONEY'
        amount = round(random.uniform(0.01, 0.02), 4)
        amount_in_wei = int(amount * 10 ** 18)

        data = from_token_name, to_token_name, amount, amount_in_wei

        result = await swap_bex(self.client.account_name, self.client.private_key,
                                self.client.proxy_init, swapdata=data)

        return result

    @helper
    async def swap_eth_bex(self):
        from functions import swap_bex

        from_token_name = 'BERA'
        to_token_name = 'WETH'
        amount = round(random.uniform(0.01, 0.02), 4)
        amount_in_wei = int(amount * 10 ** 18)

        data = from_token_name, to_token_name, amount, amount_in_wei

        result = await swap_bex(self.client.account_name, self.client.private_key,
                                self.client.proxy_init, swapdata=data)

        return result
