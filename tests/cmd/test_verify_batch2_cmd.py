import os
from pathlib import Path

from mm_mnemonic.cli.cli import app


def test_check_eth_ok(runner, output_dir):
    runner.invoke(app, ["batch2", "-c", "eth", "-b", 7, "-l", 8, "-w", 12, "-o", str(output_dir)])
    result = runner.invoke(app, ["verify-batch2", str(output_dir)])
    assert result.exit_code == 0
    assert "coin: eth" in result.output
    assert "batch count: 7" in result.output
    assert "limit: 8" in result.output
    assert "total accounts: 56" in result.output
    assert "words: 12" in result.output
    assert "verify: ok" in result.output


def test_check_btc_ok(runner, output_dir):
    runner.invoke(app, ["batch2", "-c", "btc", "-b", 5, "-l", 3, "-w", 24, "-o", str(output_dir)])
    result = runner.invoke(app, ["verify-batch2", str(output_dir)])
    assert result.exit_code == 0
    assert "coin: btc" in result.output
    assert "batch count: 5" in result.output
    assert "limit: 3" in result.output
    assert "total accounts: 15" in result.output
    assert "words: 24" in result.output
    assert "verify: ok" in result.output


def test_check_for_bad_batch_count(runner, output_dir):
    result = runner.invoke(app, ["verify-batch2", str(output_dir)])
    assert result.exit_code == 1
    assert result.stdout.strip() == "error: invalid batch2 folder, can't get batch count"


def test_check_for_inconsistent_files(runner, output_dir):
    runner.invoke(app, ["batch2", "-c", "eth", "-b", 7, "-l", 8, "-o", str(output_dir)])
    Path(os.path.join(output_dir, "addresses_1.txt")).unlink()
    result = runner.invoke(app, ["verify-batch2", str(output_dir)])
    assert result.exit_code == 1
    assert result.stdout.strip() == "error: invalid batch2 folder, inconsistent files"


def test_inconsistent_limit(runner, output_dir):
    runner.invoke(app, ["batch2", "-c", "eth", "-b", 7, "-l", 8, "-o", str(output_dir)])
    data = Path(os.path.join(output_dir, "addresses_3.txt")).read_text()
    Path(os.path.join(output_dir, "addresses_3.txt")).write_text(data + "\nnew-address")
    result = runner.invoke(app, ["verify-batch2", str(output_dir)])
    assert result.exit_code == 1
    assert result.stdout.strip() == "error: inconsistent limit"
