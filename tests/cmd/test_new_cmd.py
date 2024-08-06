from mm_mnemonic.cli.cli import app
from mm_mnemonic.cli.cli_utils import parse_keys_file
from mm_mnemonic.mnemonic import get_seed


def test_new_cmd_eth(runner):
    result = runner.invoke(app, ["new", "-c", "eth", "-l", 7])
    assert result.exit_code == 0
    keys_file = parse_keys_file(result.stdout)
    assert len(keys_file.passphrase) == 32
    assert get_seed(keys_file.mnemonic, keys_file.passphrase).hex() == keys_file.seed
    assert len(keys_file.accounts) == 7
    assert keys_file.accounts[3].path == "m/44'/60'/0'/0/3"


def test_new_cmd_btc(runner):
    result = runner.invoke(app, ["new", "-c", "btc", "-l", 7])
    assert result.exit_code == 0
    keys_file = parse_keys_file(result.stdout)
    assert len(keys_file.passphrase) == 32
    assert get_seed(keys_file.mnemonic, keys_file.passphrase).hex() == keys_file.seed
    assert len(keys_file.accounts) == 7
    assert keys_file.accounts[3].path == "m/44'/0'/0'/0/3"


def test_new_generates_different(runner):
    res1 = runner.invoke(app, ["new", "-c", "eth", "-l", 1])
    res2 = runner.invoke(app, ["new", "-c", "eth", "-l", 1])
    keys_file1 = parse_keys_file(res1.stdout)
    keys_file2 = parse_keys_file(res2.stdout)
    assert keys_file1.mnemonic != keys_file2.mnemonic


def test_no_passphrase(runner):
    # with passphrase
    result = runner.invoke(app, ["new", "-c", "eth", "-l", 7])
    assert result.exit_code == 0
    keys_file = parse_keys_file(result.stdout)
    assert len(keys_file.passphrase) > 0

    # no passphrase
    result = runner.invoke(app, ["new", "-c", "eth", "-l", 7, "--no-passphrase"])
    assert result.exit_code == 0
    keys_file = parse_keys_file(result.stdout)
    assert keys_file.passphrase == ""
