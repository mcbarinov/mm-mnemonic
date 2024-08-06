from pathlib import Path
from typing import Annotated, Union

import typer

from mm_mnemonic.cli import cli_utils
from mm_mnemonic.cli.cmd import (
    batch1_cmd,
    batch2_cmd,
    check_cmd,
    new_cmd,
    show_cmd,
    verify_batch2_cmd,
)
from mm_mnemonic.cli.cmd.batch1_cmd import Batch1CmdParams
from mm_mnemonic.cli.cmd.batch2_cmd import Batch2CmdParams
from mm_mnemonic.cli.cmd.new_cmd import NewCmdParams
from mm_mnemonic.cli.cmd.show_cmd import ShowCmdParams
from mm_mnemonic.types import Coin

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False, add_completion=False)


@app.command(name="new", help="Derive accounts from a generated mnemonic with a passphrase.")
def new_command(
    coin: Annotated[Coin, typer.Option("--coin", "-c")] = Coin.ETH,
    path_prefix: Annotated[str, typer.Option("--prefix")] = "",
    limit: Annotated[int, typer.Option("--limit", "-l")] = 10,
    no_passphrase: Annotated[bool, typer.Option("--no-passphrase", help="Empty passphrase")] = False,
    columns: Annotated[
        str,
        typer.Option("--columns", help="columns to print: all,mnemonic,passphrase,seed,path,address,private"),
    ] = "all",
) -> None:
    new_cmd.run(NewCmdParams(coin=coin, path_prefix=path_prefix, limit=limit, columns=columns, no_passphrase=no_passphrase))


@app.command(name="batch1", help="Generate batches of accounts. Each batch has its own mnemonic and password.")
def batch1_command(
    batches: Annotated[int, typer.Option("--batches", "-b", help="How many batches(files) will be generated.")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="How many accounts will be generated for a batch.")],
    output_dir: Annotated[str, typer.Option("--output-dir", "-o", help="Where to store files with the generated accounts.")],
    coin: Annotated[Coin, typer.Option("--coin", "-c")] = Coin.ETH,
    path_prefix: Annotated[str, typer.Option("--prefix")] = "",
) -> None:
    batch1_cmd.run(
        Batch1CmdParams(batches=batches, output_dir=output_dir, coin=coin, path_prefix=path_prefix, limit=limit),
    )


@app.command(name="batch2", help="Generate batches of accounts. Each account has its own mnemonic.")
def batch2_command(
    batches: Annotated[int, typer.Option("--batches", "-b", help="How many batches(files) will be generated.")],
    limit: Annotated[int, typer.Option("--limit", "-l", help="How many accounts will be generated for a batch.")],
    output_dir: Annotated[str, typer.Option("--output-dir", "-o", help="Where to store files with the generated accounts.")],
    coin: Annotated[Coin, typer.Option("--coin", "-c")] = Coin.ETH,
    path_prefix: Annotated[str, typer.Option("--prefix")] = "",
    words: Annotated[int, typer.Option("--words", "-w")] = 24,
) -> None:
    batch2_cmd.run(
        Batch2CmdParams(
            batches=batches,
            output_dir=output_dir,
            coin=coin,
            path_prefix=path_prefix,
            limit=limit,
            words=words,
        ),
    )


@app.command(name="verify-batch2", help="Verify a folder with files from the 'batch2' command.")
def verify_batch2_command(
    directory_path: Annotated[Path, typer.Argument(..., exists=True, dir_okay=True, readable=True)],
) -> None:
    verify_batch2_cmd.run(directory_path)


@app.command(name="show", help="Derive accounts from the specified mnemonic and passhprase.")
def show_command(
    coin: Annotated[Coin, typer.Option("--coin", "-c")] = Coin.ETH,
    mnemonic: Annotated[str, typer.Option("--mnemonic", "-m")] = "",
    passphrase: Annotated[Union[str, None], typer.Option("--passphrase", "-p")] = None,  # noqa: UP007
    path_prefix: Annotated[str, typer.Option("--prefix")] = "",
    limit: Annotated[int, typer.Option("--limit", "-l")] = 10,
) -> None:
    show_cmd.run(ShowCmdParams(mnemonic=mnemonic, passphrase=passphrase, coin=coin, path_prefix=path_prefix, limit=limit))


@app.command(name="check", help="Not yet implemented.")
def check_command() -> None:
    check_cmd.run()


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mm-mnemonic version: {cli_utils.get_version()}")
        raise typer.Exit()


@app.callback()
def main(_version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True)) -> None:
    pass


if __name__ == "__main__":
    app()
