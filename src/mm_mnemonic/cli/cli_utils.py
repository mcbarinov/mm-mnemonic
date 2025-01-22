import importlib.metadata
import re
from dataclasses import dataclass
from pathlib import Path

from mm_mnemonic.account import Account
from mm_mnemonic.mnemonic import get_seed


@dataclass
class KeysFile:
    mnemonic: str
    passphrase: str
    seed: str
    accounts: list[Account]


def _has_column(columns: str, search: str) -> bool:
    if columns == "all":
        return True
    return search in columns


def make_keys_output(mnemonic: str, passphrase: str, accounts: list[Account], columns: str = "all") -> str:
    result = ""
    if _has_column(columns, "mnemonic"):
        result += f"mnemonic: {mnemonic}\n"
    if _has_column(columns, "passphrase"):
        result += f"passphrase: {passphrase}\n"
    if _has_column(columns, "seed"):
        seed = get_seed(mnemonic, passphrase).hex()
        result += f"seed: {seed}\n"
    for acc in accounts:
        row = []
        if _has_column(columns, "path"):
            row.append(acc.path)
        if _has_column(columns, "address"):
            row.append(acc.address)
        if _has_column(columns, "private"):
            row.append(acc.private)
        result += " ".join(row) + "\n"

    return result.strip()


def parse_keys_file(data: str) -> KeysFile:
    lines = data.splitlines()
    if not lines[0].startswith("mnemonic: "):
        raise ValueError("data doesn't have the 'mnemonic:' line")
    mnemonic = lines[0].removeprefix("mnemonic: ")
    if not lines[1].startswith("passphrase: "):
        raise ValueError("data doesn't have the 'passphrase: ' line")
    passphrase = lines[1].removeprefix("passphrase: ")
    if not lines[2].startswith("seed: "):
        raise ValueError("data doesn't have the 'seed: ' line")
    seed = lines[2].removeprefix("seed: ")

    accounts: list[Account] = []
    for line in lines[3:]:
        acc_lines = line.split()
        acc = Account(path=acc_lines[0], address=acc_lines[1], private=acc_lines[2])
        accounts.append(acc)

    return KeysFile(mnemonic=mnemonic, passphrase=passphrase, seed=seed, accounts=accounts)


def get_max_file_number_suffix(parent_dir: Path) -> int | None:
    result = None
    for f in parent_dir.glob("*.txt"):
        res = re.match(r".*_(\d+)\.txt$", str(f.absolute()))
        if res:
            new_value = int(res.group(1))
            result = max(new_value, result) if result is not None else new_value  # type: ignore[call-overload]
    return result


def get_version() -> str:
    return importlib.metadata.version("mm-mnemonic")
