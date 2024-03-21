"""
------------------------------------------------GENERAL SETTINGS--------------------------------------------------------
    WALLETS_TO_WORK = 0 | Софт будет брать кошельки из таблице по правилам, описанным снизу
    0       = все кошельки подряд
    3       = только кошелек №3
    4, 20   = кошелек №4 и №20
    [5, 25] = кошельки с №5 по №25

    ACCOUNTS_IN_STREAM      | Количество кошельков в потоке на выполнение. Если всего 100 кошельков, а указать 10,
                                то софт сделает 10 подходов по 10 кошельков

    EXCEL_PASSWORD          | Включает запрос пароля при входе в софт. Сначала установите пароль в таблице
    EXCEL_PAGE_NAME         | Название листа в таблице. Пример: 'BeraChain'

"""
SOFTWARE_MODE = 1               # 0 - последовательный запуск / 1 - параллельный запуск
ACCOUNTS_IN_STREAM = 10         # Количество аккаунтов в потоке при SOFTWARE_MODE = 1
WALLETS_TO_WORK = 0             # 0 / 3 / 3, 20 / [3, 20]
BREAK_ROUTE = False             # Прекращает выполнение маршрута, если произойдет ошибка
SHUFFLE_WALLETS = False         # Перемешивает кошельки перед запуском
SAVE_PROGRESS = False           # Включает сохранение прогресса аккаунта для Classic-routes
TELEGRAM_NOTIFICATIONS = False  # Включает уведомления в Telegram
WAIT_FAUCET = False             # Ожидает получение $BERA из Faucet

'------------------------------------------------SLEEP CONTROL---------------------------------------------------------'
SLEEP_MODE = False               # Включает сон после каждого модуля и аккаунта
SLEEP_TIME_MODULES = (30, 60)    # (минимум, максимум) секунд | Время сна между модулями.
SLEEP_TIME_ACCOUNTS = (60, 120)  # (минимум, максимум) секунд | Время сна между аккаунтами.

'------------------------------------------------RETRY CONTROL---------------------------------------------------------'
MAXIMUM_RETRY = 20               # Количество повторений при ошибках
SLEEP_TIME_RETRY = (5, 10)       # (минимум, максимум) секунд | Время сна после очередного повторения

'------------------------------------------------PROXY CONTROL---------------------------------------------------------'
MOBILE_PROXY = False             # Включает использование мобильных прокси.
MOBILE_PROXY_URL_CHANGER = [
    '',
    '',
    ''
]  # ['link1', 'link2'..] | Ссылки для смены IP. Софт пройдется по всем ссылкам, можно указать несколько прокси в Excel

'------------------------------------------------SECURE DATA-----------------------------------------------------------'
# https://2captcha.com/enterpage
TWO_CAPTCHA_API_KEY = ""

# EXCEL AND GOOGLE INFO
EXCEL_PASSWORD = False
EXCEL_PAGE_NAME = "Berachain"

# TELEGRAM DATA
TG_TOKEN = ""  # https://t.me/BotFather
TG_ID = ""  # https://t.me/getmyid_bot

"""
--------------------------------------------CLASSIC-ROUTES CONTROL------------------------------------------------------

    mint_berachain_tokens           # минт $BERA на BeraChain Faucet (https://artio.faucet.berachain.com/)
    swap_btc_bex                    # свап на BEX ($BERA -> $BTC)
    swap_honey_bex                  # свап на BEX ($BERA -> $HONEY)
    swap_stgusdc_bex                # свап на BEX ($BERA -> $STGUSDC)
    swap_eth_bex                    # свап на BEX ($BERA -> $ETH)
    deposit_honey_berps             # добавление $HONEY ликвидности на Berps           
    supply_honey_bend               # добавление $HONEY ликвидности на Bend           
    supply_btc_bend                 # добавление $BTC ликвидности на Bend      
    supply_eth_bend                 # добавление $ETH ликвидности на Bend      
    withdraw_honey_bend             # вывод $HONEY ликвидности на Bend         
    withdraw_btc_bend               # вывод $BTC ликвидности на Bend           
    withdraw_eth_bend               # вывод $ETH ликвидности на Bend           
    add_liqiudity_bex_honey_mim     # добавление $HONEY/MIM ликвидности на BEX 
    add_liqiudity_bex_bera_usdc     # добавление $BERA/USDC ликвидности на BEX
    mint_honey                      # минт $HONEY за $STGUSDC
    mint_domain                     # минт домена на https://www.beranames.com/
    mint_booga_ticket               # минт OOGA BOOGA Ticket за 4.2 $HONEY
    mint_bera_red                   # минт  Mint BERA RED ENVELOPE за 1.8 $HONEY
    claim_bgt_on_berps              # клейм $BGT на Berps Dashboard
    delegate_bgt_on_station         # делегирование $BGT на BeraChain Station
    vote_bgt_on_station             # голосование на BeraChain Station
    claim_galxe_points              # выполнение дейлика на Galxe (5 поинтов за визит Faucet)
    claim_galxe_campaign_points     # выполнение кампании на Galxe (55 поинтов, без Twiiter и Discord )

    Выберите необходимые модули для взаимодействия
    Вы можете создать любой маршрут, софт отработает строго по нему. Для каждого списка будет выбран один модуль в
    маршрут, если софт выберет None, то он пропустит данный список модулей. 
    Список модулей сверху.

    CLASSIC_ROUTES_MODULES_USING = [
        ['mint_berachain_tokens'],
        ['swap_stgusdc_bex'],
        ['mint_honey'],
        ['claim_galxe_points']
        ...
    ]
"""
CLASSIC_ROUTES_MODULES_USING = [
    ['mint_berachain_tokens'],
    ['swap_stgusdc_bex'],
    ['swap_eth_bex', 'swap_btc_bex'],
    ['add_liqiudity_bex_bera_usdc'],
    ['mint_honey'],
    ['mint_booga_ticket', None],
    ['supply_honey_bend', 'supply_btc_bend', 'supply_eth_bend'],
    ['claim_galxe_points'],
    ['claim_bgt_on_berps'],
    ['delegate_bgt_on_station'],
    ['vote_bgt_on_station'],
    ['claim_galxe_campaign_points'],
]
