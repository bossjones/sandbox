"""
ci tasks
"""
import logging
from invoke import task, call
import click
from tasks.utils import get_compose_env

# from tasks.core import clean, execute_sql

from .utils import (
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_CAUTION,
    COLOR_STABLE,
)

# from tasks.core import clean, execute_sql
from tweetpik_cli.dbx_logger import get_logger  # noqa: E402

# from tweetpik_cli.utils.parser import get_domain_from_fqdn

LOGGER = get_logger(__name__, provider="Invoke view", level=logging.INFO)


@task(incrementable=["verbose"])
def config(ctx, loc="local"):
    """
    Open coverage report inside of browser
    Usage: inv view.config
    """
    env = get_compose_env(ctx, loc=loc)

    # Only display result
    ctx.config["run"]["echo"] = True

    # Override run commands env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = r"code ~/.config/tweetpik_cli/settings.toml"

    ctx.run(_cmd)
