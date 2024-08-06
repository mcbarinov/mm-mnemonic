from eth_account import Account as EthAccount

from mm_mnemonic.account import Account

DEFAULT_ETH_PATH_PREFIX = "m/44'/60'/0'/0/"

EthAccount.enable_unaudited_hdwallet_features()


def derive_account(mnemonic: str, passphrase: str, path: str) -> Account:
    acc = EthAccount.from_mnemonic(mnemonic, passphrase=passphrase, account_path=path)
    private_key = acc.key.hex()
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    return Account(address=acc.address, private=private_key, path=path)
