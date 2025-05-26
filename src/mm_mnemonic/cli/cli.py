from pathlib import Path
from typing import Annotated, Union

import typer

from mm_mnemonic.cli import cli_utils, commands
from mm_mnemonic.cli.commands.batch1 import Batch1CmdParams
from mm_mnemonic.cli.commands.batch2 import Batch2CmdParams
from mm_mnemonic.cli.commands.new import NewCmdParams
from mm_mnemonic.cli.commands.show import ShowCmdParams
from mm_mnemonic.types import Coin

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False, add_completion=False)


DerivationPathOption = Annotated[
    str | None,
    typer.Option(
        "--derivation-path",
        help="The derivation path to use (e.g., m/44'/0'/0'/0/{i}). If not specified, a default path will be used.",
    ),
]
CoinOption = Annotated[Coin, typer.Option("--coin", "-c")]
LimitOption = Annotated[int, typer.Option("--limit", "-l", help="How many accounts to derive")]


def mnemonic_words_callback(value: int) -> int:
    if value not in [12, 15, 21, 24]:
        raise typer.BadParameter("Words must be one of: 12, 15, 21, 24")
    return value


@app.command(name="new", help="Derive accounts from a generated mnemonic with a passphrase.")
def new_command(
    coin: CoinOption = Coin.ETH,
    limit: LimitOption = 10,
    derivation_path: DerivationPathOption = None,
    words: Annotated[
        int, typer.Option("--words", "-w", callback=mnemonic_words_callback, help="How many words to generate: 12, 15, 21, 24")
    ] = 24,
    no_passphrase: Annotated[bool, typer.Option("--no-passphrase", help="Empty passphrase")] = False,
    columns: Annotated[
        str,
        typer.Option("--columns", help="columns to print: all,mnemonic,passphrase,seed,path,address,private"),
    ] = "all",
) -> None:
    commands.new.run(
        NewCmdParams(
            coin=coin, derivation_path=derivation_path, limit=limit, columns=columns, no_passphrase=no_passphrase, words=words
        )
    )


@app.command(name="batch1", help="Generate batches of accounts. Each batch has its own mnemonic and password.")
def batch1_command(
    batches: Annotated[int, typer.Option("--batches", "-b", help="How many batches(files) will be generated.")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="How many accounts will be generated for a batch.")],
    output_dir: Annotated[str, typer.Option("--output-dir", "-o", help="Where to store files with the generated accounts.")],
    coin: CoinOption = Coin.ETH,
    derivation_path: DerivationPathOption = None,
) -> None:
    commands.batch1.run(
        Batch1CmdParams(batches=batches, output_dir=output_dir, coin=coin, derivation_path=derivation_path, limit=limit),
    )


@app.command(name="batch2", help="Generate batches of accounts. Each account has its own mnemonic.")
def batch2_command(
    batches: Annotated[int, typer.Option("--batches", "-b", help="How many batches(files) will be generated.")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="How many accounts will be generated for a batch.")],
    output_dir: Annotated[str, typer.Option("--output-dir", "-o", help="Where to store files with the generated accounts.")],
    coin: CoinOption = Coin.ETH,
    derivation_path: DerivationPathOption = None,
    words: Annotated[int, typer.Option("--words", "-w")] = 24,
) -> None:
    commands.batch2.run(
        Batch2CmdParams(
            batches=batches,
            output_dir=output_dir,
            coin=coin,
            derivation_path=derivation_path,
            limit=limit,
            words=words,
        ),
    )


@app.command(name="verify-batch2", help="Verify a folder with files from the 'batch2' command.")
def verify_batch2_command(
    directory_path: Annotated[Path, typer.Argument(..., exists=True, dir_okay=True, readable=True)],
) -> None:
    commands.verify_batch2.run(directory_path)


@app.command(name="show", help="Derive accounts from the specified mnemonic and passhprase.")
def show_command(
    coin: CoinOption = Coin.ETH,
    mnemonic: Annotated[str, typer.Option("--mnemonic", "-m")] = "",
    passphrase: Annotated[Union[str, None], typer.Option("--passphrase", "-p")] = None,  # noqa: UP007
    derivation_path: DerivationPathOption = None,
    limit: LimitOption = 10,
) -> None:
    commands.show.run(
        ShowCmdParams(mnemonic=mnemonic, passphrase=passphrase, coin=coin, derivation_path=derivation_path, limit=limit)
    )


@app.command(name="check", help="Not yet implemented.")
def check_command() -> None:
    commands.check.run()


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mm-mnemonic version: {cli_utils.get_version()}")
        raise typer.Exit


@app.callback()
def main(_version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True)) -> None:
    pass


if __name__ == "__main__":
    app()
