import asyncio
import json

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
            'authority': 'artio-80085-ts-faucet-api-2.berachain.com',
            'accept': '*/*',
            'accept-language': 'en-En,zh;q=0.9',
            'authorization': f'Bearer {captcha_key}',
            'cache-control': 'no-cache',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://artio.faucet.berachain.com',
            'pragma': 'no-cache',
            'referer': 'https://artio.faucet.berachain.com/',
        }

        params = {
            'address': self.client.address
        }

        await self.make_request(method="POST", url=url, params=params, data=json.dumps(params), headers=headers)

        self.logger_msg(*self.client.acc_info, msg=f'$BERA was successfully claimed on faucet', type_msg='success')
