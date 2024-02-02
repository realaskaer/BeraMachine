import io
import os
import sys
import random
import asyncio
import functools
import traceback
import msoffcrypto
import pandas as pd

from getpass import getpass
from termcolor import cprint
from web3.exceptions import TimeExhausted
from msoffcrypto.exceptions import DecryptionError, InvalidKeyError

from general_settings import (
    SLEEP_TIME,
    SLEEP_TIME_RETRY,
    MAXIMUM_RETRY,
    EXCEL_PASSWORD,
    EXCEL_PAGE_NAME
)


async def sleep(self, min_time=SLEEP_TIME[0], max_time=SLEEP_TIME[1]):
    duration = random.randint(min_time, max_time)
    print()
    self.logger_msg(*self.client.acc_info, msg=f"💤 Sleeping for {duration} seconds")
    await asyncio.sleep(duration)


def get_accounts_data():
    try:
        decrypted_data = io.BytesIO()
        with open('./data/accounts_data.xlsx', 'rb') as file:
            if EXCEL_PASSWORD:
                cprint('⚔️ Enter the password degen', color='light_blue')
                password = getpass()
                office_file = msoffcrypto.OfficeFile(file)

                try:
                    office_file.load_key(password=password)
                except msoffcrypto.exceptions.DecryptionError:
                    cprint('\n⚠️ Incorrect password to decrypt Excel file! ⚠️', color='light_red', attrs=["blink"])
                    raise DecryptionError('Incorrect password')

                try:
                    office_file.decrypt(decrypted_data)
                except msoffcrypto.exceptions.InvalidKeyError:
                    cprint('\n⚠️ Incorrect password to decrypt Excel file! ⚠️', color='light_red', attrs=["blink"])
                    raise InvalidKeyError('Incorrect password')

                except msoffcrypto.exceptions.DecryptionError:
                    cprint('\n⚠️ Set password on your Excel file first! ⚠️', color='light_red', attrs=["blink"])
                    raise DecryptionError('Excel without password')

                office_file.decrypt(decrypted_data)

                try:
                    wb = pd.read_excel(decrypted_data, sheet_name=EXCEL_PAGE_NAME)
                except ValueError as error:
                    cprint('\n⚠️ Wrong page name! ⚠️', color='light_red', attrs=["blink"])
                    raise ValueError(f"{error}")
            else:
                try:
                    wb = pd.read_excel(file, sheet_name=EXCEL_PAGE_NAME)
                except ValueError as error:
                    cprint('\n⚠️ Wrong page name! ⚠️', color='light_red', attrs=["blink"])
                    raise ValueError(f"{error}")

            accounts_data = {}
            for index, row in wb.iterrows():
                account_name = row["Name"]
                private_key = row["Private Key"]
                proxy = row["Proxy"]
                email_address = row['Email Address']
                email_password = row['Email Password']

                accounts_data[int(index) + 1] = {
                    "account_number": account_name,
                    "private_key": private_key,
                    "proxy": proxy,
                    "email_address": email_address,
                    "email_password": email_password,
                }

            acc_names, private_keys, proxies, email_addresses, email_passwords = [], [], [], [], []
            for k, v in accounts_data.items():
                acc_names.append(v['account_number'] if isinstance(v['account_number'], (int, str)) else None)
                private_keys.append(v['private_key'])
                proxies.append(v['proxy'] if isinstance(v['proxy'], str) else None)
                email_addresses.append(v['email_address'] if isinstance(v['email_address'], str) else None)
                email_passwords.append(v['email_password'] if isinstance(v['email_password'], str) else None)

            acc_names = [str(item) for item in acc_names if item is not None]
            proxies = [item for item in proxies if item is not None]
            email_addresses = [item for item in email_addresses if item is not None]
            email_passwords = [item for item in email_passwords if item is not None]

            return acc_names, private_keys, proxies, email_addresses, email_passwords
    except (DecryptionError, InvalidKeyError, DecryptionError, ValueError):
        sys.exit()

    except ImportError:
        cprint(f'\nAre you sure about EXCEL_PASSWORD in general_settings.py?', color='light_red')
        sys.exit()

    except Exception as error:
        cprint(f'\nError in <get_accounts_data> function! Error: {error}\n', color='light_red')
        sys.exit()

def clean_progress_file():
    with open('./data/services/wallets_progress.json', 'w') as file:
        file.truncate(0)


def check_progress_file():
    file_path = './data/services/wallets_progress.json'

    if os.path.getsize(file_path) > 0:
        return True
    else:
        return False


def helper(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        from modules.interfaces import PriceImpactException, BlockchainException, SoftwareException
        attempts = 0
        error = None
        stop_flag = False
        try:
            while attempts <= MAXIMUM_RETRY:
                try:
                    return await func(self, *args, **kwargs)
                except (PriceImpactException, BlockchainException, SoftwareException,
                        asyncio.exceptions.TimeoutError, TimeExhausted, ValueError) as err:
                    error = err
                    attempts += 1

                except Exception as err:
                    error = err
                    attempts += 1
                    traceback.print_exc()
                finally:
                    msg = f'{error} | Try[{attempts}/{MAXIMUM_RETRY + 1}]'
                    if attempts:
                        if isinstance(error, asyncio.exceptions.TimeoutError):
                            error = 'Connection to RPC is not stable'

                        if isinstance(error, BlockchainException):
                            if 'insufficient funds' in str(error):
                                stop_flag = True
                                network_name = self.client.network.name
                                msg = f'Insufficient funds on {network_name}, software will stop this action\n'
                            else:
                                self.logger_msg(
                                    self.client.account_name,
                                    None, msg=f'Maybe problem with node: {self.client.rpc}', type_msg='warning')
                                await self.client.change_rpc()

                        self.logger_msg(self.client.account_name, None, msg=msg, type_msg='error')

                        if stop_flag:
                            break

                        await sleep(self, *SLEEP_TIME_RETRY)

                        if attempts > MAXIMUM_RETRY:
                            self.logger_msg(self.client.account_name,
                                            None, msg=f"Tries are over, software will stop module\n", type_msg='error')
        finally:
            await self.client.session.close()
        return False

    return wrapper
