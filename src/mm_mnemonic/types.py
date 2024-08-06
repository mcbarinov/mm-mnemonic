from enum import Enum, unique


@unique
class Coin(str, Enum):
    BTC = "btc"  # bitcoin
    ETH = "eth"  # ethereum
    SOL = "sol"  # solana
