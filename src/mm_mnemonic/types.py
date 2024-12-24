from enum import Enum, unique


@unique
class Coin(str, Enum):
    BTC = "btc"  # bitcoin
    BTC_TESTNET = "btc_testnet"  # bitcoin testnet
    ETH = "eth"  # ethereum
    SOL = "sol"  # solana


@unique
class MnemonicWords(int, Enum):
    TWELVE = 12
    FIFTEEN = 15
    EIGHTEEN = 18
    TWENTY_ONE = 21
    TWENTY_FOUR = 24
