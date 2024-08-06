from mm_mnemonic.cli.cli import app


def test_show_cmd_eth(runner):
    result = runner.invoke(app, ["new", "-c", "eth", "-l", 7])
    assert result.exit_code == 0
    assert "m/44'/60'/0'/0/6" in result.output
