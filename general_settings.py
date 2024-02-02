"""
------------------------------------------------GENERAL SETTINGS--------------------------------------------------------
    WALLETS_TO_WORK = 0 | Софт будет брать кошельки из таблице по правилам, описаным снизу
    0       = все кошельки подряд
    3       = только кошелек №3
    4, 20   = кошелек №4 и №20
    [5, 25] = кошельки с №5 по №25

    ACCOUNTS_IN_STREAM      | Количество кошельков в потоке на выполнение. Если всего 100 кошельков, а указать 10,
                                то софт сделает 10 подходов по 10 кошельков

    EXCEL_PASSWORD          | Включает запрос пароля при входе в софт. Сначала установите пароль в таблице
    EXCEL_PAGE_NAME         | Название листа в таблице. Пример: 'BeraChain'
    EMAIL_DOMAIN | Здесь нужно указать домен от ваших почт. Пример 123@rambler.ru (все что после @ является доменом)

"""
EMAIL_DOMAIN = 'rambler.ru'
SOFTWARE_MODE = 0               # 0 - последовательный запуск / 1 - параллельный запуск
ACCOUNTS_IN_STREAM = 1          # Только для SOFTWARE_MODE = 1 (параллельный запуск)
WALLETS_TO_WORK = 0             # 0 / 3 / 3, 20 / [3, 20]
SHUFFLE_WALLETS = False         # Перемешивает кошельки перед запуском
SAVE_PROGRESS = False           # True или False | Включает сохранение прогресса аккаунта для Classic-routes
TELEGRAM_NOTIFICATIONS = False  # True или False | Включает уведомления в Telegram

'------------------------------------------------SLEEP CONTROL---------------------------------------------------------'
SLEEP_MODE = False               # True или False | Включает сон после каждого модуля и аккаунта
SLEEP_TIME = (10, 15)           # (минимум, максимум) секунд | Время сна между модулями.
SLEEP_TIME_STREAM = (5, 10)    # (минимум, максимум) секунд | Время сна между аккаунтами.

'------------------------------------------------RETRY CONTROL---------------------------------------------------------'
MAXIMUM_RETRY = 3               # Количество повторений при ошибках
SLEEP_TIME_RETRY = (5, 10)      # (минимум, максимум) секунд | Время сна после очередного повторения

'------------------------------------------------PROXY CONTROL---------------------------------------------------------'
MOBILE_PROXY = False             # True или False | Включает использование мобильных прокси.
MOBILE_PROXY_URL_CHANGER = ['',
                            '',
                            '']  # ['link1', 'link2'..] | Ссылки для смены IP

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

    mint_berachain_tokens  # минт $BERA на BeraChain Faucet (https://artio.faucet.berachain.com/)
    swap_btc_bex           # свап на BEX ($BERA -> $BTC)
    swap_honey_bex         # свап на BEX ($BERA -> $HONEY)
    swap_stgusdc_bex       # свап на BEX ($BERA -> $STGUSDC)
    add_liqiudity_bex      # добавление ликвидности на BEX
    mint_honey             # минт $HONEY за $STGUSDC
    mint_booga_ticket      # минт OOGA BOOGA Ticket за 4.2 $HONEY
    claim_galxe_points     # выполнение дейлика на Galxe (5 поинтов за визит Faucet)

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
    ['add_liqiudity_bex'],
    ['mint_honey'],
    ['claim_galxe_points']
]
