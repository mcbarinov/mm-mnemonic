import os.path
import shutil

from mm_mnemonic.cli.cli import app
from tests.conftest import create_random_output_dir


def test_batch2_cmd(runner):
    output_dir = create_random_output_dir()
    try:
        result = runner.invoke(app, ["batch2", "-c", "eth", "-b", 7, "-l", "10", "-w", 12, "-o", output_dir])
        assert result.exit_code == 0

        # it generates correct files
        generated_files = [f.absolute() for f in output_dir.iterdir()]
        assert all([f.is_file() for f in generated_files])
        assert {str(f) for f in generated_files} == set().union(
            [os.path.join(output_dir.absolute(), f"keys_{f}.txt") for f in range(1, 8)],
            [os.path.join(output_dir.absolute(), f"addresses_{f}.txt") for f in range(1, 8)],
            [os.path.join(output_dir.absolute(), f"mnemonics_{f}.txt") for f in range(1, 8)],
        )

    finally:
        shutil.rmtree(output_dir)
