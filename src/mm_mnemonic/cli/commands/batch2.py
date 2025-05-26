from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from mm_mnemonic.account import DerivedAccount, derive_account, get_default_derivation_path
from mm_mnemonic.mnemonic import generate_mnemonic
from mm_mnemonic.types import Coin


@dataclass
class Batches:
    @dataclass
    class Key:
        path: str
        address: str
        private: str
        mnemonic: str

    batches: int  # count of batches
    addresses: list[list[str]]
    mnemonics: list[list[str]]
    keys: list[list[Key]]

    def is_valid(self) -> bool:
        # check batches count
        batches_ok = self.batches == len(self.addresses) == len(self.mnemonics) == len(self.keys)
        if not batches_ok:
            return False

        # check limit
        if not self.addresses:
            return False
        limit = len(self.addresses[0])
        for batch_number in range(self.batches):
            limit_ok = (
                limit == len(self.addresses[batch_number]) == len(self.mnemonics[batch_number]) == len(self.keys[batch_number])
            )
            if not limit_ok:
                return False

        return True


@dataclass
class Batch2CmdParams:
    batches: int
    output_dir: str
    coin: Coin
    derivation_path: str | None
    words: int
    limit: int

    def __post_init__(self) -> None:
        output_dir = Path(self.output_dir).expanduser()
        output_dir.mkdir(exist_ok=True, parents=True)
        self.output_dir = str(output_dir)


def run(params: Batch2CmdParams) -> None:
    for i in range(params.batches):
        _process_batch(i + 1, params)
    typer.echo("done")


def _process_batch(batch_number: int, params: Batch2CmdParams) -> None:
    accounts: list[DerivedAccount] = []
    mnemonics: list[str] = []
    path_prefix = params.derivation_path
    if not path_prefix:
        path_prefix = get_default_derivation_path(params.coin)

    for _ in range(params.limit):
        mnemonic = generate_mnemonic(params.words)
        mnemonics.append(mnemonic)
        account = derive_account(params.coin, mnemonic, "", path_prefix.replace("{i}", "0"))
        accounts.append(account)

    # write keys file
    data = ""
    for acc, mnemo in zip(accounts, mnemonics, strict=True):
        data += f"{acc.path} {acc.address} {acc.private} {mnemo}\n"
    Path(params.output_dir + f"/keys_{batch_number}.txt").write_text(data)

    # write address file
    data = "\n".join([a.address for a in accounts]) + "\n"
    Path(params.output_dir + f"/addresses_{batch_number}.txt").write_text(data)

    # write mnemonics
    data = "\n".join(mnemonics)
    Path(params.output_dir + f"/mnemonics_{batch_number}.txt").write_text(data)

    typer.echo(f"file {batch_number}: ok")
