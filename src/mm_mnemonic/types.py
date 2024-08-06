from enum import Enum, unique


@unique
class Coin(str, Enum):
    BTC = "btc"  # bitcoin
    BTC_TESTNET = "btc_testnet"  # bitcoin testnet
    ETH = "eth"  # ethereum
    SOL = "sol"  # solana
