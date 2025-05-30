import sys
from pathlib import Path

import typer
from pydantic import BaseModel

from mm_mnemonic import output
from mm_mnemonic.account import derive_accounts
from mm_mnemonic.mnemonic import generate_mnemonic, is_valid_mnemonic
from mm_mnemonic.network import check_network_security
from mm_mnemonic.passphrase import generate_passphrase, prompt_encryption_password
from mm_mnemonic.types import Coin


class Params(BaseModel):
    coin: Coin
    mnemonic: str | None
    passphrase: str | None
    generate: bool  # Generate a new mnemonic
    generate_passphrase: bool  # Generate a passphrase too, would be used only if --generate is set
    prompt: bool  # Prompt for mnemonic and passphrase
    words: int
    derivation_path: str | None
    limit: int
    output_dir: Path | None
    encrypt: bool  # Encrypt keys.toml in output_dir
    allow_internet_risk: bool  # Allow running with internet connection

    def validate_params(self) -> None:
        # Output validation
        if self.encrypt and self.output_dir is None:
            raise typer.BadParameter(
                "Cannot use --encrypt without --output-dir. Use --output-dir to specify where to save encrypted files."
            )

        # Input method conflicts (mutually exclusive)
        input_methods = [("prompt", self.prompt), ("generate", self.generate), ("mnemonic", self.mnemonic is not None)]
        active_methods = [(name, active) for name, active in input_methods if active]

        if len(active_methods) > 1:
            method_names = [name for name, _ in active_methods]
            raise typer.BadParameter(
                f"Cannot use multiple input methods simultaneously: {', '.join(method_names)}. "
                f"Choose one: --prompt, --generate, or --mnemonic."
            )

        # Passphrase validation
        if self.prompt and self.passphrase is not None:
            raise typer.BadParameter(
                "Cannot use --passphrase with --prompt. In prompt mode, passphrase will be asked interactively."
            )

        # Generate-specific validations
        if self.generate_passphrase and not self.generate:
            raise typer.BadParameter(
                "--generate-passphrase can only be used with --generate. Use: --generate --generate-passphrase"
            )

        # Words validation (only matters when generating)
        if not self.generate and self.words != 24:  # 24 is the default
            raise typer.BadParameter("--words can only be used with --generate. Use: --generate --words 12")


def run(params: Params) -> None:
    params.validate_params()
    try:
        if params.prompt:
            check_network_security(params.allow_internet_risk)
            while True:
                mnemonic = typer.prompt("Mnemonic", hide_input=True)
                if is_valid_mnemonic(mnemonic):
                    break
                typer.echo("invalid mnemonic")
            passphrase = typer.prompt("Passphrase", hide_input=True, default="")
        elif params.generate:
            check_network_security(params.allow_internet_risk)
            mnemonic = generate_mnemonic(params.words)
            passphrase = (
                generate_passphrase()
                if params.generate_passphrase
                else typer.prompt("Passphrase", hide_input=True, confirmation_prompt=True, default="")
            )
        elif params.mnemonic is not None:
            check_network_security(params.allow_internet_risk)
            mnemonic = params.mnemonic
            passphrase = params.passphrase or ""
        else:
            show_derive_examples()
            sys.exit(1)

        derived_accounts = derive_accounts(
            coin=params.coin,
            mnemonic=mnemonic,
            passphrase=passphrase,
            derivation_path=params.derivation_path,
            limit=params.limit,
        )

        if params.output_dir:
            encryption_password = None
            if params.encrypt:
                encryption_password = prompt_encryption_password()
            output.store_derived_accounts(derived_accounts, params.output_dir, encryption_password)

        # Don't show sensitive information on screen when saving to files
        show_sensitive = params.output_dir is None
        output.print_derived_accounts(derived_accounts, show_sensitive=show_sensitive)
    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes for security warnings
        raise
    except Exception as e:
        typer.echo(str(e))
        sys.exit(1)


def show_derive_examples() -> None:
    """Display helpful examples of how to use the derive command."""
    typer.echo("""mm-mnemonic derive - Generate cryptocurrency accounts from BIP39 mnemonic phrases

USAGE EXAMPLES:

1. Interactive mode (prompt for mnemonic and passphrase):
   mm-mnemonic derive --prompt

2. Generate new random mnemonic:
   mm-mnemonic derive --generate

3. Generate new mnemonic AND passphrase:
   mm-mnemonic derive --generate --generate-passphrase

4. Use specific mnemonic and passphrase:
   mm-mnemonic derive --mnemonic="abandon abandon abandon..." --passphrase="secret"

ADDITIONAL OPTIONS:
   --coin         Choose cryptocurrency (BTC, ETH, SOL, TRX) [default: ETH]
   --limit        Number of accounts to derive [default: 10]
   --output-dir   Save accounts to files
   --encrypt      Encrypt saved keys

MORE EXAMPLES:
   # Derive 5 Bitcoin accounts and save encrypted
   mm-mnemonic derive --generate --coin BTC --limit 5 --output-dir ./btc-keys --encrypt

   # Use custom derivation path
   mm-mnemonic derive --prompt --derivation-path "m/44'/60'/0'/0/{i}"

   # Generate 12-word mnemonic
   mm-mnemonic derive --generate --words 12

For detailed help: mm-mnemonic derive --help""")
