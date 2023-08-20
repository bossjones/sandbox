"""
git tasks
"""
import logging
from invoke import task
import click
from tasks.utils import get_compose_env

# from tasks.core import clean, execute_sql

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


# git rev-parse HEAD


# @task(incrementable=["verbose"])
# def verbosity(ctx, loc="local", quiet=False, verbose=0):
#     """
#     Return `git rev-parse HEAD` for project.
#     Usage: inv docker.lint-test or inv local.lint-test
#     """
#     env = get_compose_env(ctx, loc=loc)

#     # Only display result
#     ctx.config["run"]["echo"] = False

#     # Override run commands env variables one key at a time
#     for k, v in env.items():
#         ctx.config["run"]["env"][k] = v


@task(incrementable=["verbose"])
def pr_sha(ctx, loc="local", quiet=False, verbose=0):
    """
    Return `git rev-parse HEAD` for project.
    Usage: inv docker.lint-test or inv local.lint-test
    """
    env = get_compose_env(ctx, loc=loc)

    # Only display result
    ctx.config["run"]["echo"] = False

    # Override run commands env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    res = ctx.run("git rev-parse HEAD")

    # override CI_IMAGE value
    ctx.config["run"]["env"]["PR_SHA"] = f"{res.stdout}"
    ctx.config["run"]["env"]["REPO_NAME"] = "bossjones/dancedetector-ci"
    ctx.config["run"]["env"][
        "IMAGE_TAG"
    ] = f'{ctx.config["run"]["env"]["REPO_NAME"]}:{ctx.config["run"]["env"]["PR_SHA"]}'
    ctx.config["run"]["env"]["TAG"] = ctx.config["run"]["env"]["IMAGE_TAG"]

    if verbose >= 1:
        msg = f'[PR_SHA] {ctx.config["run"]["env"]["PR_SHA"]}'
        click.secho(msg, fg="green")
