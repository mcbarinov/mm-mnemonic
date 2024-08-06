from eth_account.hdaccount import Mnemonic


def generate_mnemonic(words: int = 24) -> str:
    m = Mnemonic("english")
    return m.generate(words)


def get_seed(mnemonic: str, passphrase: str) -> bytes:
    return Mnemonic.to_seed(mnemonic, passphrase)


def is_valid_mnemonic(mnemonic: str) -> bool:
    return Mnemonic("english").is_mnemonic_valid(mnemonic)
