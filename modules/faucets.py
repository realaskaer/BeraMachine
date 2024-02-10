import asyncio

from web3.exceptions import TransactionNotFound

from general_settings import TWO_CAPTCHA_API_KEY
from modules import Logger, RequestClient
from modules.interfaces import SoftwareException
from utils.tools import helper


class Faucet(Logger, RequestClient):
    def __init__(self, client):
        self.client = client
        Logger.__init__(self)

    async def swap(self):
        pass

    async def create_task_for_captcha(self):
        url = 'https://api.2captcha.com/createTask'

        payload = {
            "clientKey": TWO_CAPTCHA_API_KEY,
            "task": {
                "type": "RecaptchaV3TaskProxyless",
                "websiteURL": "https://artio.faucet.berachain.com/",
                "websiteKey": "6LfOA04pAAAAAL9ttkwIz40hC63_7IsaU2MgcwVH",
                "minScore": 0.9,
                "pageAction": "submit"
            }
        }

        response = await self.make_request(method="POST", url=url, json=payload)

        if not response['errorId']:
            return response['taskId']
        raise SoftwareException('Bad request to 2Captcha(Create Task)')

    async def get_captcha_key(self, task_id):
        url = 'https://api.2captcha.com/getTaskResult'

        payload = {
            "clientKey": TWO_CAPTCHA_API_KEY,
            "taskId": task_id
        }

        total_time = 0
        timeout = 360
        while True:
            response = await self.make_request(method="POST", url=url, json=payload)

            if response['status'] == 'ready':
                return response['solution']['gRecaptchaResponse']

            total_time += 5
            await asyncio.sleep(5)

            if total_time > timeout:
                raise SoftwareException('Can`t get captcha solve in 360 second')

    @helper
    async def claim_berachain_tokens(self):

        self.logger_msg(*self.client.acc_info, msg=f'Claiming $BERA on faucet')

        url = 'https://artio-80085-faucet-api-recaptcha.berachain.com/api/claim'

        task_id = await self.create_task_for_captcha()
        captcha_key = await self.get_captcha_key(task_id)

        headers = {
            "authority": "artio-80085-faucet-api-recaptcha.berachain.com",
            "method": "POST",
            "path": f"/api/claim?address={self.client.address}",
            "scheme": "https",
            "accept": "*/*",
            "accept-Encoding": "gzip, deflate, br",
            "accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "authorization": f"Bearer {captcha_key}",
            "content-type": "application/json",
            "origin": "https://artio.faucet.berachain.com",
            "referer": "https://artio.faucet.berachain.com/",
            "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "sec-ch-ua-Mobile": "?0",
            "sec-ch-ua-Platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }

        params = {
            "address": f"{self.client.address}"
        }

        response = (await self.make_request(method="POST", url=url, params=params, json=params, headers=headers))['msg']

        self.logger_msg(*self.client.acc_info, msg=f'$BERA was successfully claimed on faucet', type_msg='success')

        self.logger_msg(*self.client.acc_info, msg=f'Waiting to receive $BERA from faucet')

        tx_hash = response.split()[-1]

        poll_latency = 60
        while True:
            try:
                receipts = await self.client.w3.eth.get_transaction_receipt(tx_hash)

                status = receipts.get("status")
                if status == 1:
                    message = f'Transaction was successful: {self.client.explorer}tx/{tx_hash}'
                    self.logger_msg(*self.client.acc_info, msg=message, type_msg='success')
                    return True
                elif status is None:
                    self.logger_msg(*self.client.acc_info, msg=f'Still waiting $BERA from faucet', type_msg='warning')
                    await asyncio.sleep(poll_latency)
                else:
                    raise SoftwareException(f'Transaction failed: {self.client.explorer}tx/{tx_hash}')
            except TransactionNotFound:
                self.logger_msg(*self.client.acc_info, msg=f'Still waiting $BERA from faucet', type_msg='warning')
                await asyncio.sleep(poll_latency)
            except Exception as error:
                self.logger_msg(
                    *self.client.acc_info, msg=f'RPC got autims response. Error: {error}', type_msg='warning')
                await asyncio.sleep(poll_latency)
