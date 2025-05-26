from mm_mnemonic.account import DerivedAccount

DEFAULT_DERIVATION_PATH = "m/44'/501'/{i}'/0'"


def derive_account(mnemonic: str, passphrase: str, path: str) -> DerivedAccount:
    raise NotImplementedError
