from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import NoReturn

import typer

from mm_mnemonic.account import derive_account
from mm_mnemonic.cli import cli_utils
from mm_mnemonic.types import Coin


@dataclass
class Batch:
    @dataclass
    class Key:
        path: str
        address: str
        private: str
        mnemonic: str

    addresses: list[str]
    mnemonics: list[str]
    keys: list[Key]


def run(directory_path: Path) -> None:
    directory_path = directory_path.expanduser()
    batch_count = _check_batch_count(directory_path)
    _check_inconsistent_files(directory_path, batch_count)
    batches = _read_batches(directory_path, batch_count)
    limit = _check_limit(batches)
    total_accounts = _check_total_accounts(batches, batch_count=batch_count, limit=limit)
    _check_doubles(batches)
    words_count = _check_word_count(batches)
    coin = _get_coin(batches)
    for batch in batches:
        _check_batch_accounts(batch, coin)
    result = f"coin: {coin.value}\nbatch count: {batch_count}\nlimit: {limit}\ntotal accounts: {total_accounts}\n"
    result += f"words: {words_count}\nverify: ok"
    typer.echo(result)


def _check_batch_count(directory_path: Path) -> int:
    batch_count = cli_utils.get_max_file_number_suffix(directory_path)
    if batch_count is None or batch_count == 0:
        _exit("invalid batch2 folder, can't get batch count")
    return batch_count


def _check_inconsistent_files(directory_path: Path, batches: int) -> None:
    all_files = set(directory_path.iterdir())

    addresses = [directory_path / f"addresses_{i}.txt" for i in range(1, batches + 1)]
    mnemonics = [directory_path / f"mnemonics_{i}.txt" for i in range(1, batches + 1)]
    keys = [directory_path / f"keys_{i}.txt" for i in range(1, batches + 1)]
    needed_files = set(addresses).union(mnemonics).union(keys)

    if all_files != needed_files:
        _exit("invalid batch2 folder, inconsistent files")


def _read_batches(directory_path: Path, batch_count: int) -> list[Batch]:
    try:
        batches = []
        for i in range(1, batch_count + 1):
            # addresses
            data = (directory_path / f"addresses_{i}.txt").read_text().strip()
            addresses = data.splitlines()

            # mnemonics
            data = (directory_path / f"mnemonics_{i}.txt").read_text().strip()
            mnemonics = data.splitlines()

            # keys
            keys = []
            data = (directory_path / f"keys_{i}.txt").read_text().strip()
            for row in data.splitlines():
                arr = row.split()
                path = arr[0]
                address = arr[1]
                private = arr[2]
                mnemonic = " ".join(arr[3:])
                keys.append(Batch.Key(path=path, address=address, private=private, mnemonic=mnemonic))

            batches.append(Batch(addresses=addresses, mnemonics=mnemonics, keys=keys))
        return batches  # noqa: TRY300
    except Exception as _:
        _exit("can't parse batches")


def _check_limit(batches: list[Batch]) -> int:
    limit = len(batches[0].addresses)
    addresses_ok = all(len(b.addresses) == limit for b in batches)
    mnemonics_ok = all(len(b.mnemonics) == limit for b in batches)
    keys_ok = all(len(b.keys) == limit for b in batches)
    if addresses_ok and mnemonics_ok and keys_ok:
        return limit
    _exit("inconsistent limit")


def _check_word_count(batches: list[Batch]) -> int:
    word_count = {len(m.split()) for m in list(chain.from_iterable([b.mnemonics for b in batches]))}
    if len(word_count) != 1:
        _exit("invalid word count")
    return word_count.pop()


def _check_total_accounts(batches: list[Batch], *, batch_count: int, limit: int) -> int:
    total_addresses = len(list(chain.from_iterable([b.addresses for b in batches])))
    total_mnemonics = len(list(chain.from_iterable([b.mnemonics for b in batches])))
    total_keys = len(list(chain.from_iterable([b.keys for b in batches])))
    if batch_count * limit == total_addresses == total_mnemonics == total_keys:
        return total_keys
    _exit("invalid total accounts")


def _check_doubles(batches: list[Batch]) -> None:
    # mnemonics
    all_mnemonics = list(chain.from_iterable([b.mnemonics for b in batches]))
    if len(all_mnemonics) != len(set(all_mnemonics)):
        _exit("account doubles")
    # addresses
    all_addresses = list(chain.from_iterable([b.addresses for b in batches]))
    if len(all_addresses) != len(set(all_addresses)):
        _exit("account doubles")


def _get_coin(batches: list[Batch]) -> Coin:
    path = batches[0].keys[0].path
    if path.startswith("m/44'/0'/"):
        return Coin.BTC
    if path.startswith("m/44'/60'/"):
        return Coin.ETH
    _exit("invalid coin path")


def _check_batch_accounts(batch: Batch, coin: Coin) -> None:
    for i, address in enumerate(batch.addresses):
        mnemonic = batch.mnemonics[i]
        key = batch.keys[i]
        acc = derive_account(coin, mnemonic, "", key.path)
        if acc.address != address or acc.private != key.private or acc.path != key.path:
            _exit(f"invalid account: {address}")


def _exit(message: str) -> NoReturn:
    typer.echo(f"error: {message}")
    raise typer.Exit(code=1)
