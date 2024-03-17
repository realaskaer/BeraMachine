class Network:
    def __init__(
            self,
            name: str,
            rpc: list,
            chain_id: int,
            eip1559_support: bool,
            token: str,
            explorer: str,
            decimals: int = 18
    ):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.eip1559_support = eip1559_support
        self.token = token
        self.explorer = explorer
        self.decimals = decimals

    def __repr__(self):
        return f'{self.name}'


BeraChainRPC = Network(
    name='BeraChain',
    rpc=[
        'https://artio.rpc.berachain.com/'
    ],
    chain_id=80085,
    eip1559_support=True,
    token='BERA',
    explorer='https://testnet.beratrail.io/'
)
