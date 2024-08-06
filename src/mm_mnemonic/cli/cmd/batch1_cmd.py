from dataclasses import dataclass
from pathlib import Path

import typer

from mm_mnemonic.account import derive_accounts
from mm_mnemonic.mnemonic import generate_mnemonic, get_seed
from mm_mnemonic.passphrase import generate_passphrase
from mm_mnemonic.types import Coin


@dataclass
class Batch1CmdParams:
    batches: int
    output_dir: str
    coin: Coin
    path_prefix: str
    limit: int

    def __post_init__(self) -> None:
        output_dir = Path(self.output_dir).expanduser()
        output_dir.mkdir(exist_ok=True, parents=True)
        self.output_dir = str(output_dir)


def run(params: Batch1CmdParams) -> None:
    for i in range(params.batches):
        _process_file(i + 1, params)
    typer.echo("done")


def _process_file(batch_number: int, params: Batch1CmdParams) -> None:
    mnemonic = generate_mnemonic()
    passphrase = generate_passphrase()
    seed = get_seed(mnemonic, passphrase).hex()
    accounts = derive_accounts(
        coin=params.coin,
        mnemonic=mnemonic,
        passphrase=passphrase,
        path_prefix=params.path_prefix,
        limit=params.limit,
    )

    # write key file
    data = f"mnemonic: {mnemonic}\npassphrase: {passphrase}\nseed: {seed}\n"
    for acc in accounts:
        data += f"{acc.path} {acc.address} {acc.private}\n"
    Path(params.output_dir + f"/keys_{batch_number}.txt").write_text(data)

    # write address file
    data = "\n".join([a.address for a in accounts]) + "\n"
    Path(params.output_dir + f"/addresses_{batch_number}.txt").write_text(data)

    typer.echo(f"file {batch_number}: ok")
