from dataclasses import dataclass

import typer

from mm_mnemonic.account import derive_accounts
from mm_mnemonic.cli import cli_utils
from mm_mnemonic.mnemonic import generate_mnemonic
from mm_mnemonic.passphrase import generate_passphrase
from mm_mnemonic.types import Coin


@dataclass
class NewCmdParams:
    coin: Coin
    path_prefix: str
    limit: int
    columns: str
    words: int
    no_passphrase: bool

    def __post_init__(self) -> None:
        self.columns = self.columns.lower().strip()

    def has_column(self, value: str) -> bool:
        return self.columns == "all" or value in self.columns


def run(params: NewCmdParams) -> None:
    mnemonic = generate_mnemonic(params.words)
    passphrase = "" if params.no_passphrase else generate_passphrase()
    accounts = derive_accounts(
        coin=params.coin,
        mnemonic=mnemonic,
        passphrase=passphrase,
        path_prefix=params.path_prefix,
        limit=params.limit,
    )
    typer.echo(cli_utils.make_keys_output(mnemonic, passphrase, accounts, params.columns))
