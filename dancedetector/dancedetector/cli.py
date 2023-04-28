"""cerebro_bot.cli"""
from __future__ import annotations

import logging
import sys
from typing import (
    Optional,
)

from IPython.core import ultratb
import rich
from rich.pretty import pprint
import typer

from dancedetector.dbx_logger import (
    get_logger,
    intercept_all_loggers,
    global_log_config
)

sys.excepthook = ultratb.FormattedTB(
    mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
)
############################################

# https://github.com/whoisandy/k2s3/blob/6e0d24abb837add1d7fcc20619533c603ea76b22/k2s3/cli.py#L114

# LOGGER = get_logger(__name__, provider="CLI", level=logging.DEBUG)
# intercept_all_loggers()

global_log_config(
    log_level=logging.getLevelName("DEBUG"),
    json=False,
)


CACHE_CTX = {}

# When you create an CLI = typer.Typer() it works as a group of commands.
CLI = typer.Typer(name="dancedetectorctl", callback=CACHE_CTX)


@CLI.command()
def hello(ctx: typer.Context, name: Optional[str] = typer.Option(None)) -> None:
    """
    Dummy command
    """
    typer.echo(f"Hello {name}")


@CLI.command()
def dump_context(ctx: typer.Context) -> typer.Context:
    """
    Dump Context
    """
    typer.echo("\nDumping context:\n")
    pprint(ctx.meta)
    return ctx


@CLI.command()
def config_dump(ctx: typer.Context) -> typer.Context:
    """
    Dump Cerebro config info to STD out
    """
    assert ctx.meta
    typer.echo("\nDumping config:\n")


@CLI.command()
def doctor(ctx: typer.Context) -> typer.Context:
    """
    Doctor checks your environment to verify it is ready to run Cerebro
    """
    assert ctx.meta
    typer.echo("\nRunning Doctor ...\n")


@CLI.command()
def async_dump_context(ctx: typer.Context) -> None:
    """
    Dump Context
    """
    typer.echo("\nDumping context:\n")
    pprint(ctx.meta)



@CLI.command()
def run(ctx: typer.Context) -> None:
    """
    Run dancedetector
    """
    typer.echo("\ndancedetector:\n")


class DanceDetectorContext:
    """_summary_

    Returns:
        _type_: _description_
    """

    @classmethod
    def create(
        cls,
        ctx: typer.Context,
        debug: bool = True,
        run_bot: bool = True,
        run_web: bool = True,
        run_metrics: bool = True,
        run_aiodebug: bool = False,
    ) -> "DanceDetectorContext":
        """_summary_

        Args:
            ctx (typer.Context): _description_
            debug (bool, optional): _description_. Defaults to True.
            run_bot (bool, optional): _description_. Defaults to True.
            run_web (bool, optional): _description_. Defaults to True.
            run_metrics (bool, optional): _description_. Defaults to True.
            run_aiodebug (bool, optional): _description_. Defaults to False.

        Returns:
            DanceDetectorContext: _description_
        """
        # ctx.ensure_object(dict)

        self = DanceDetectorContext()
        self.ctx = ctx
        self.debug = debug
        self.run_bot = run_bot
        self.run_web = run_web
        self.run_metrics = run_metrics
        self.run_aiodebug = run_aiodebug
        self.debug = debug
        return self


@CLI.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
        "auto_envvar_prefix": "CEREBRO",
    }
)
@CLI.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    debug: bool = True,
    run_bot: bool = True,
    run_web: bool = True,
    run_metrics: bool = True,
    run_aiodebug: bool = False,
) -> typer.Context:
    """
    Manage users in the awesome CLI app.
    """

    ctx.ensure_object(dict)
    # ctx.obj = await DanceDetectorContext.create(
    #     ctx, debug, run_bot, run_web, run_metrics, run_aiodebug
    # )

    # SOURCE: http://click.palletsprojects.com/en/7.x/commands/?highlight=__main__
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below
    # asyncio.run(co_get_ctx_improved(ctx))

    ctx.meta["DEBUG"] = debug
    ctx.obj["DEBUG"] = debug

    ctx.meta["AIOMONITOR"] = run_metrics
    ctx.obj["AIOMONITOR"] = run_metrics

    for extra_arg in ctx.args:
        typer.echo(f"Got extra arg: {extra_arg}")
    typer.echo(f"About to execute command: {ctx.invoked_subcommand}")
    return ctx


if __name__ == "__main__":
    _ctx = CLI()
    rich.print("CTX")
    rich.print(_ctx)
