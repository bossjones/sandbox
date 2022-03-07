"""
program tasks
"""
import logging
from invoke import task
from tasks.utils import get_compose_env

logger = logging.getLogger(__name__)


@task
def get_crud_interfaces(ctx, loc="local"):
    """
    Display all crud interfactes for tweetpik_cli
    Usage: inv program.get-crud-interfaces
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = "grep \",\" tweetpik_cli/api/crud/__init__.py | grep -v \"^#\" | tr ',' '\n' | /usr/bin/xargs"

    res = ctx.run(_cmd)

    return res.stdout


@task
def env(ctx, loc="local"):
    """
    Display shell env
    Usage: inv program.env
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = "env"

    ctx.run(_cmd)
