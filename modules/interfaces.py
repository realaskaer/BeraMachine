import asyncio
import aiohttp.client_exceptions
from loguru import logger
from sys import stderr
from datetime import datetime
from abc import ABC
from config import CHAIN_NAME


class PriceImpactException(Exception):
    pass


class BlockchainException(Exception):
    pass


class SoftwareException(Exception):
    pass


class SoftwareExceptionWithoutRetry(Exception):
    pass


class WrongGalxeCode(Exception):
    pass


class Logger(ABC):
    def __init__(self):
        self.logger = logger
        self.logger.remove()
        logger_format = "<cyan>{time:HH:mm:ss}</cyan> | <level>" "{level: <8}</level> | <level>{message}</level>"
        self.logger.add(stderr, format=logger_format)
        date = datetime.today().date()
        self.logger.add(f"./data/logs/{date}.log", rotation="500 MB", level="INFO", format=logger_format)

    def logger_msg(self, account_name, address, msg, type_msg: str = 'info'):
        if account_name is None and address is None:
            info = f'[BeraMachine] | {CHAIN_NAME[1]} | {self.__class__.__name__} |'
        elif account_name is not None and address is None:
            info = f'[{account_name}] | {CHAIN_NAME[1]} | {self.__class__.__name__} |'
        else:
            info = f'[{account_name}] | {address} | {CHAIN_NAME[1]} | {self.__class__.__name__} |'
        if type_msg == 'info':
            self.logger.info(f"{info} {msg}")
        elif type_msg == 'error':
            self.logger.error(f"{info} {msg}")
        elif type_msg == 'success':
            self.logger.success(f"{info} {msg}")
        elif type_msg == 'warning':
            self.logger.warning(f"{info} {msg}")


class RequestClient(ABC):
    def __init__(self, client):
        self.client = client

    async def make_request(self, method:str = 'GET', url:str = None, headers:dict = None, params: dict = None,
                           data:str = None, json:dict = None, module_name:str = 'Request'):

        errors = None

        total_time = 0
        timeout = 360
        while True:
            try:
                async with self.client.session.request(
                        method=method, url=url, headers=headers, data=data, params=params, json=json
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        if isinstance(data, dict):
                            errors = data.get('errors')
                        elif isinstance(data, list) and isinstance(data[0], dict):
                            errors = data[0].get('errors')

                        if not errors:
                            return data
                        elif 'have been marked as inactive' in f"{errors}":
                            raise SoftwareExceptionWithoutRetry(
                                f"Bad request to {self.__class__.__name__}({module_name}) API: {errors[0]['message']}")
                        else:
                            raise SoftwareException(
                                f"Bad request to {self.__class__.__name__}({module_name}) API: {errors[0]['message']}")

                    raise SoftwareException(
                        f"Bad request to {self.__class__.__name__}({module_name}) API: {await response.text()}")
            except aiohttp.client_exceptions.ServerDisconnectedError as error:
                total_time += 15
                await asyncio.sleep(15)
                if total_time > timeout:
                    raise SoftwareException(error)
                continue
            except SoftwareExceptionWithoutRetry as error:
                raise SoftwareExceptionWithoutRetry(error)
            except Exception as error:
                raise SoftwareException(error)
