from dataclasses import dataclass

from mm_mnemonic.types import Coin


@dataclass
class Account:
    address: str
    private: str
    path: str


def is_address_matched(address: str, search_pattern: str | None) -> bool:
    if search_pattern is None:
        return False
    address = address.lower()
    search_pattern = search_pattern.lower()

    if search_pattern.count("*") == 0:
        return address == search_pattern
    if search_pattern.startswith("*"):
        return address.endswith(search_pattern.removeprefix("*"))
    if search_pattern.endswith("*"):
        return address.startswith(search_pattern.removesuffix("*"))

    start_address, end_address = search_pattern.split("*")
    return address.startswith(start_address) and address.endswith(end_address)


def derive_accounts(coin: Coin, mnemonic: str, passphrase: str, path_prefix: str | None, limit: int) -> list[Account]:
    if not path_prefix:
        path_prefix = get_default_path_prefix(coin)
    if not path_prefix.endswith("/"):
        path_prefix = path_prefix + "/"

    return [derive_account(coin, mnemonic, passphrase, path=f"{path_prefix}{i}") for i in range(limit)]


def derive_account(coin: Coin, mnemonic: str, passphrase: str, path: str) -> Account:
    from mm_mnemonic import btc, eth

    match coin:
        case Coin.BTC:
            return btc.derive_account(mnemonic, passphrase, path)
        case Coin.BTC_TESTNET:
            return btc.derive_account(mnemonic, passphrase, path, testnet=True)
        case Coin.ETH:
            return eth.derive_account(mnemonic, passphrase, path)
        case _:
            raise NotImplementedError


def get_default_path_prefix(coin: Coin) -> str:
    from mm_mnemonic import btc, eth

    match coin:
        case Coin.BTC:
            return btc.DEFAULT_BTC_PATH_PREFIX
        case Coin.BTC_TESTNET:
            return btc.DEFAULT_BTC_TESTNET_PATH_PREFIX
        case Coin.ETH:
            return eth.DEFAULT_ETH_PATH_PREFIX
        case _:
            raise NotImplementedError
