import getpass
from dataclasses import dataclass

import typer

from mm_mnemonic.account import derive_accounts
from mm_mnemonic.cli import cli_utils
from mm_mnemonic.mnemonic import is_valid_mnemonic
from mm_mnemonic.types import Coin


@dataclass
class ShowCmdParams:
    mnemonic: str
    passphrase: str | None
    coin: Coin
    path_prefix: str
    limit: int


def run(params: ShowCmdParams) -> None:
    mnemonic = params.mnemonic
    while True:
        if not is_valid_mnemonic(mnemonic):
            mnemonic = getpass.getpass("mnemonic")
            if is_valid_mnemonic(mnemonic):
                break
            else:
                typer.echo("invalid mnemonic")
        else:
            break

    passphrase = getpass.getpass("passphrase") if params.passphrase is None else params.passphrase

    accounts = derive_accounts(
        coin=params.coin,
        mnemonic=mnemonic,
        passphrase=passphrase,
        path_prefix=params.path_prefix,
        limit=params.limit,
    )
    typer.echo(cli_utils.make_keys_output(mnemonic, passphrase, accounts))
