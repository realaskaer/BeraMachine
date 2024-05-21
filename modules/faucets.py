import asyncio

from general_settings import TWO_CAPTCHA_API_KEY
from modules import Logger, RequestClient, Client
from modules.interfaces import SoftwareException
from utils.tools import helper, sleep


class Faucet(Logger, RequestClient):
    def __init__(self, client: Client):
        self.client = client
        Logger.__init__(self)

    async def swap(self):
        pass

    async def create_task_for_captcha(self):
        url = 'https://api.2captcha.com/createTask'

        proxy_tuple = self.client.proxy_init.split('@')

        proxy_login, proxy_password = proxy_tuple[0].split(':')
        proxy_address, proxy_port = proxy_tuple[1].split(':')

        payload = {
            "clientKey": TWO_CAPTCHA_API_KEY,
            "task": {
                "type": "TurnstileTask",
                "websiteURL": "https://artio.faucet.berachain.com/",
                "websiteKey": "0x4AAAAAAARdAuciFArKhVwt",
                "userAgent": self.client.session.headers['User-Agent'],
                "proxyType": "http",
                "proxyAddress": proxy_address,
                "proxyPort": proxy_port,
                "proxyLogin": proxy_login,
                "proxyPassword": proxy_password
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
                return response['solution']['token']

            total_time += 5
            await asyncio.sleep(5)

            if total_time > timeout:
                raise SoftwareException('Can`t get captcha solve in 360 second')

    @helper
    async def claim_berachain_tokens(self):

        self.logger_msg(*self.client.acc_info, msg=f'Claiming $BERA on faucet')

        url = 'https://artio-80085-faucet-api-cf.berachain.com/api/claim'

        task_id = await self.create_task_for_captcha()
        captcha_key = await self.get_captcha_key(task_id)

        headers = {
            "accept": "*/*",
            "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "authorization": f"Bearer {captcha_key}",
            "content-type": "text/plain;charset=UTF-8",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"123\", \"Chromium\";v=\"123\", \"Not.A/Brand\";v=\"23\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "referrer": "https://artio.faucet.berachain.com/",
            "referrerPolicy": "strict-origin-when-cross-origin",
            "body": f"{{\"address\":\"{self.client.address}\"}}",
            "method": "POST",
            "mode": "cors",
            "credentials": "include"
        }

        params = {
            "address": f"{self.client.address}"
        }

        await self.make_request(method="POST", url=url, params=params, json=params, headers=headers)
        self.logger_msg(*self.client.acc_info, msg=f'$BERA was successfully claimed on faucet', type_msg='success')
        self.logger_msg(
            *self.client.acc_info, msg=f'You’ll receive BERA in your wallet in about 2 minutes', type_msg='warning'
        )

        await sleep(self, 150, 200)

        return True
