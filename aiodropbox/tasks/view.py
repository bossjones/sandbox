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

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


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

    _cmd = r"code ~/.config/aiodropbox/settings.toml"

    ctx.run(_cmd)
