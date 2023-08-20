"""
local tasks
"""
import logging
from invoke import task, call
from invoke.exceptions import Exit
import pathlib

# from sqlalchemy.engine.url import make_url
import click
from tasks.utils import get_compose_env

# from dancedetector.utils import iops
from tasks import iops
from .utils import (
    COLOR_SUCCESS,
    COLOR_CAUTION,
)
import rich

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


@task(incrementable=["verbose"])
def get_env(ctx, loc="local", verbose=0):
    """
    Get environment vars necessary to run fastapi
    Usage: inv local.get-env
    """
    env = get_compose_env(ctx, loc=loc)

    # Only display result
    ctx.config["run"]["echo"] = False

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    for key in env:
        print("{0}={1}".format(key, env[key]))


@task(incrementable=["verbose"])
def get_python_path(ctx, loc="local", verbose=0):
    """
    Get environment vars necessary to run fastapi
    Usage: inv local.get-python-path
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = 'python -c "import sys; print(sys.executable)"'
    ctx.run(_cmd)


@task(incrementable=["verbose"])
def ipython(ctx, loc="local", verbose=0):
    """
    Start up ipython
    Usage: inv local.ipython
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = "ipython"
    ctx.run(_cmd)


@task(incrementable=["verbose"])
def detect_os(ctx, loc="local", verbose=0):
    """
    detect what type of os we are using
    Usage: inv local.detect-os
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    res_os = ctx.run("uname -s")
    ctx.config["run"]["env"]["OS"] = f"{res_os.stdout}"

    if ctx.config["run"]["env"]["OS"] == "Windows_NT":
        ctx.config["run"]["env"]["DETECTED_OS"] = "Windows"
    else:
        ctx.config["run"]["env"]["DETECTED_OS"] = ctx.config["run"]["env"]["OS"]

    if verbose >= 1:
        msg = f'[detect-os] Detected: {ctx.config["run"]["env"]["DETECTED_OS"]}'
        click.secho(msg, fg=COLOR_SUCCESS)

    if ctx.config["run"]["env"]["DETECTED_OS"] == "Darwin":
        ctx.config["run"]["env"]["ARCHFLAGS"] = "-arch x86_64"
        ctx.config["run"]["env"]["PKG_CONFIG_PATH"] = "/usr/local/opt/libffi/lib/pkgconfig"
        ctx.config["run"]["env"]["LDFLAGS"] = "-L/usr/local/opt/openssl/lib"
        ctx.config["run"]["env"]["CFLAGS"] = "-I/usr/local/opt/openssl/include"


# @task(pre=[call(detect_os, loc="local")], incrementable=["verbose"])
# def serve(ctx, loc="local", verbose=0, cleanup=False):
#     """
#     start up fastapi application
#     Usage: inv local.serve
#     """
#     env = get_compose_env(ctx, loc=loc)

#     # Override run commands' env variables one key at a time
#     for k, v in env.items():
#         ctx.config["run"]["env"][k] = v

#     if verbose >= 1:
#         msg = "[serve] override env vars 'SERVER_NAME' and 'SERVER_HOST' - We don't want to mess w/ '.env.dist' for this situation"
#         click.secho(msg, fg=COLOR_SUCCESS)

#     # override CI_IMAGE value
#     ctx.config["run"]["env"]["SERVER_NAME"] = "localhost:8000"
#     ctx.config["run"]["env"]["SERVER_HOST"] = "http://localhost:8000"
#     ctx.config["run"]["env"]["BETTER_EXCEPTIONS"] = "1"

#     _cmd = r"""
# pkill -f "uvicorn app.main:app --reload" || true
# pgrep -f "uvicorn app.main:app --reload" || true
#     """

#     if verbose >= 1:
#         msg = "[serve] kill running app server: "
#         click.secho(msg, fg=COLOR_SUCCESS)

#         msg = "{}".format(_cmd)
#         click.secho(msg, fg=COLOR_SUCCESS)

#     ctx.run(_cmd)

#     # ctx.run("pip install -e .")
#     ctx.run("alembic --raiseerr upgrade head")
#     # ctx.run("python ./dancedetector/api/backend_pre_start.py")
#     # ctx.run("python ./dancedetector/initial_data.py")
#     # ctx.run("python dancedetector/dev_serve.py")
#     ctx.run("uvicorn app.main:app --reload")


# @task(pre=[call(detect_os, loc="local")], incrementable=["verbose"])
# def web(ctx, loc="local", verbose=0, cleanup=False, app_only=False):
#     """
#     start up fastapi application
#     Usage: inv local.web
#     """
#     env = get_compose_env(ctx, loc=loc)

#     # Override run commands' env variables one key at a time
#     for k, v in env.items():
#         ctx.config["run"]["env"][k] = v

#     if verbose >= 1:
#         msg = "[serve] override env vars 'SERVER_NAME' and 'SERVER_HOST' - We don't want to mess w/ '.env.dist' for this situation"
#         click.secho(msg, fg=COLOR_SUCCESS)

#     # override CI_IMAGE value
#     # ctx.config["run"]["env"]["SERVER_NAME"] = "localhost:8000"
#     # ctx.config["run"]["env"]["SERVER_HOST"] = "http://localhost:8000"
#     ctx.config["run"]["env"]["BETTER_EXCEPTIONS"] = "1"

#     if verbose >= 3:
#         click.secho(
#             "Detected 4 or more verbose flags, enabling TRACE mode", fg=COLOR_WARNING
#         )
#         # TODO: recreate web.py as your application runner
#         ctx.config["run"]["env"]["ULTRON_ENVIRONMENT"] = "development"

#     _cmd = r"""
# pkill -f "uvicorn app.main:app --reload" || true
# pgrep -f "uvicorn app.main:app --reload" || true
#     """

#     if verbose >= 1:
#         msg = "[serve] kill running app server: "
#         click.secho(msg, fg=COLOR_SUCCESS)

#         msg = "{}".format(_cmd)
#         click.secho(msg, fg=COLOR_SUCCESS)

#     ctx.run(_cmd)

#     if not app_only:
#         # ctx.run("pip install -e .")
#         ctx.run("alembic --raiseerr upgrade head")
#         # ctx.run("python ./dancedetector/api/backend_pre_start.py")
#         # ctx.run("python ./dancedetector/initial_data.py")
#         # ctx.run("python ./dancedetector/initial_data.py")
#     else:
#         click.secho("APP ONLY MODE DETECTED.", fg=COLOR_WARNING)

#     ctx.run("uvicorn app.main:app --reload")


@task(pre=[call(detect_os, loc="local")], incrementable=["verbose"], aliases=["install"])
def bootstrap(ctx, loc="local", verbose=0, cleanup=False, upgrade=False):
    """
    start up fastapi application
    Usage: inv local.bootstrap
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    if verbose >= 1:
        msg = "[install] Create virtual environment, initialize it, install packages, and remind user to activate after make is done"
        click.secho(msg, fg=COLOR_SUCCESS)

    # pip install pre-commit
    # pre-commit install -f --install-hooks
    if upgrade:
        _cmd = r"""
pip install -U -r requirements.txt
pip install -U -r requirements-dev.txt
pip install -U -r requirements-test.txt
pip install -U -r requirements-doc.txt
        """
    else:
        _cmd = r"""
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-test.txt
pip install -r requirements-doc.txt
        """

    if verbose >= 1:
        msg = "[install] Install dependencies: "
        click.secho(msg, fg=COLOR_SUCCESS)

        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)

    click.secho(
        "[install] install editable version of dancedetector",
        fg=COLOR_SUCCESS,
    )
    ctx.run("pip install -e .")


@task(pre=[call(detect_os, loc="local")], incrementable=["verbose"])
def freeze(ctx, loc="local", verbose=0, after=False, diff=False):
    """
    Write freeze.before.txt or freeze.after.txt
    Usage: inv local.freeze
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    if verbose >= 1:
        msg = "[freeze] Create virtual environment, initialize it, install packages, and remind user to activate after make is done"
        click.secho(msg, fg=COLOR_SUCCESS)

    if after:
        _cmd = r"""
pip freeze > freeze.after.txt
        """
    else:
        _cmd = r"""
pip freeze > freeze.before.txt
        """

    if verbose >= 1:
        msg = "[freeze] freeze deps: "
        click.secho(msg, fg=COLOR_SUCCESS)

        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)

    if diff:
        res = ctx.run("diff -y --suppress-common-lines freeze.before.txt freeze.after.txt")
        msg = "[freeze] diff between two freeze files: "
        click.secho(msg, fg=COLOR_SUCCESS)
        print(res.stdout)


@task(
    pre=[call(detect_os, loc="local")],
    incrementable=["verbose"],
    aliases=["pip_compile"],
)
def pip_deps(ctx, loc="local", verbose=0, cleanup=False, upgrade=False):
    """
    lock fastapi pip dependencies [requirements, dev, test]
    Usage: inv local.pip_deps
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    if verbose >= 1:
        msg = "[pip-deps] Create virtual environment, initialize it, install packages, and remind user to activate after make is done"
        click.secho(msg, fg=COLOR_SUCCESS)

    if upgrade:
        _cmd = r"""
pip-compile --output-file requirements.txt requirements.in --upgrade
pip-compile --output-file requirements-dev.txt requirements-dev.in --upgrade
pip-compile --output-file requirements-test.txt requirements-test.in --upgrade
    """
    else:
        _cmd = r"""
pip-compile --output-file requirements.txt requirements.in
pip-compile --output-file requirements-dev.txt requirements-dev.in
pip-compile --output-file requirements-test.txt requirements-test.in
    """

    if verbose >= 1:
        msg = "[pip-deps] Install dependencies: "
        click.secho(msg, fg=COLOR_SUCCESS)

        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)


@task(
    pre=[call(detect_os, loc="local")],
    incrementable=["verbose"],
)
def pip_tools(
    ctx,
    loc="local",
    verbose=0,
    cleanup=False,
    upgrade=False,
    package="",
    dev=False,
    test=False,
    dry_run=False,
):
    """
    upgrade single requirements.txt file [requirements, dev, test]
    Usage: inv local.pip-tools --upgrade --package="MonkeyType" --dev -vvv
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    if verbose >= 1:
        msg = "[pip-tools] Create virtual environment, initialize it, install packages, and remind user to activate after make is done"
        click.secho(msg, fg=COLOR_SUCCESS)

    _cmd = r"pip-compile"

    if upgrade and package:
        if verbose >= 1:
            msg = f"[pip-tools] Looks like we're upgrading a specific package: '{package}'"
            click.secho(msg, fg=COLOR_SUCCESS)
        _cmd += f" --upgrade-package '{package}'"

    if dev:
        if verbose >= 1:
            msg = "[pip-tools] output file will be DEV"
            click.secho(msg, fg=COLOR_SUCCESS)
        _cmd += " --output-file requirements-dev.txt requirements-dev.in"

    if test:
        if verbose >= 1:
            msg = "[pip-tools] output file will be TEST"
            click.secho(msg, fg=COLOR_SUCCESS)
        _cmd += " --output-file requirements-test.txt requirements-test.in"

    if (not test) and (not dev):
        if verbose >= 1:
            msg = "[pip-tools] output file will be regular requirements.txt"
            click.secho(msg, fg=COLOR_SUCCESS)
        _cmd += " --output-file requirements.txt requirements.in"

    if verbose >= 1:
        msg = "[pip-tools] Rendering dependencies ... "
        click.secho(msg, fg=COLOR_SUCCESS)

        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    if dev and test:
        msg = "Can't use both --dev and --test\n" "Please pick one or neither\n\n"
        raise Exit(msg)

    if dry_run:
        click.secho(
            f"[pip-tools] DRY RUN mode enabled, not executing command: {_cmd}",
            fg=COLOR_CAUTION,
        )
    else:
        ctx.run(_cmd)

    if upgrade and package:
        msg = "[pip-tools] Upgrading packages"
        click.secho(msg, fg=COLOR_SUCCESS)

        _upgrade_cmd = f"pip install -U {package}"

        if dry_run:
            click.secho(
                f"[pip-tools] DRY RUN mode enabled, not executing command: {_upgrade_cmd}",
                fg=COLOR_CAUTION,
            )
        else:
            ctx.run(_upgrade_cmd)


@task(pre=[call(detect_os, loc="local")], incrementable=["verbose"], aliases=["hacking"])
def contrib(ctx, loc="local", verbose=0, cleanup=False):
    """
    Install contrib files in correct places
    Usage: inv local.contrib
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    if verbose >= 1:
        msg = "[contrib] Create virtual environment, initialize it, install packages, and remind user to activate after make is done"
        click.secho(msg, fg=COLOR_SUCCESS)

    _cmd = r"""
cp -fv ./contrib/.pdbrc ~/.pdbrc
cp -fv ./contrib/.pdbrc.py ~/.pdbrc.py
mkdir -p ~/ptpython/ || true
cp -fv ./contrib/.ptpython_config.py ~/ptpython/config.py
    """

    if verbose >= 1:
        msg = "[contrib] Install configs: "
        click.secho(msg, fg=COLOR_SUCCESS)

        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)


@task(pre=[call(detect_os, loc="local")], incrementable=["verbose"])
def rsync(ctx, loc="local", verbose=0, cleanup=False):
    """
    rsync over files to ~vagrant/dancedetector folder
    Usage: inv local.rsync
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = r"""
cd && rsync -r --exclude dancedetector_venv --exclude .vagrant --exclude .git --exclude .env /srv/vagrant_repos/dancedetector/ ~/dancedetector/ && sudo chown vagrant:vagrant -R ~vagrant && cd ~/dancedetector && ls -lta
    """

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)


@task(pre=[call(detect_os, loc="local")], incrementable=["verbose"])
def clean(ctx, loc="local", verbose=0, cleanup=False):
    """
    clean compiled python artifacts
    Usage: inv local.clean
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = r"""
find . -name '*.pyc' -exec rm -fv {} +
find . -name '*.pyo' -exec rm -fv {} +
find . -name '__pycache__' -exec rm -frv {} +
    """

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)


def remove_dashes(txt: str) -> str:
    return txt.replace("-", "_")


def remove_comma(txt: str) -> str:
    return txt.replace(",", "_")


def remove_parenthesis(txt: str) -> str:
    cleaned = txt.replace("(", "_")
    return cleaned.replace(")", "_")


def remove_period(txt: str) -> str:
    return txt.replace(".", "_")


def remove_folder_name(txt: str) -> str:
    cleaned = txt.replace(":", "")
    rich.print(cleaned)
    cleaned0 = cleaned.replace(";", "")
    rich.print(cleaned0)
    cleaned1 = cleaned0.replace("?", "")
    rich.print(cleaned1)
    cleaned2 = cleaned1.replace("(", "")
    rich.print(cleaned2)
    cleaned3 = cleaned2.replace(")", "")
    rich.print(cleaned3)
    cleaned4 = cleaned3.replace("-", "_")
    rich.print(cleaned4)
    cleaned5 = cleaned4.replace(",", "")
    rich.print(cleaned5)
    cleaned6 = cleaned5.replace(".", "")
    rich.print(cleaned6)
    cleaned7 = cleaned6.replace("\t", "_")
    rich.print(cleaned7)
    cleaned8 = cleaned7.replace(" ", "_")
    rich.print(cleaned8)
    return cleaned8.lower()


def clean_name(txt: str) -> str:
    return txt.replace("-", "_")


@task(pre=[call(detect_os, loc="local")], incrementable=["verbose"])
def clean_dir_names(ctx, loc="local", verbose=0, cleanup=False, filename="", overwrite=False):
    """
    clean compiled python artifacts
    Usage: inv local.clean
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    content = iops.read_file(filename) if filename else []
    click.secho("[ content]", fg=COLOR_SUCCESS)
    rich.print(content)
    new_content = []

    for c in content:
        cleaned = remove_folder_name(c)
        # rich.print(c)
        new_content.append(cleaned)

    rich.print(new_content)

    if overwrite:
        final_file = iops.write_file(filename, contents_list=new_content)

    rich.print(final_file)


def walk_dir_media(directory: str = "", silent=True):
    media_list_only = []

    if directory and pathlib.Path(directory).is_dir():
        tree_list = iops.tree(pathlib.Path(directory), silent=silent)
        media_list_only = iops.filter_media(tree_list)
    return media_list_only


# TODO: Make a compare function like this
# SOURCE: https://github.com/twittman/Montage_compare/blob/main/src/_Montage_text_2.sh


@task(pre=[call(detect_os, loc="local")], incrementable=["verbose"])
def smaller(
    ctx,
    loc="local",
    verbose=0,
    percentage=80,
    filename="",
    directory="",
    remove_old=False,
    print_only=False,
):
    """
    clean compiled python artifacts
    Usage: inv local.smaller
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = ""

    # images
    if filename and pathlib.Path(filename).suffix in iops.IMAGE_EXTENSIONS:
        p = pathlib.Path(filename)
        _cmd = f"""magick convert {filename} -resize {percentage}% {p.stem}_smaller{p.suffix}\n"""
        if remove_old:
            _cmd += f"rm -fv {filename}\n"
    # video
    elif filename and pathlib.Path(filename).suffix in iops.VIDEO_EXTENSIONS:
        p = pathlib.Path(filename)

        _cmd = f"""
ffmpeg -y -hide_banner -loglevel warning -i \"{filename}\" -vf "scale=128:128:force_original_aspect_ratio=decrease,pad=128:128:-1:-1:color=white,setdar=1:1" \"{p.stem}_smaller{p.suffix}\"
        """
        if remove_old:
            _cmd += f"rm -fv {filename}\n"
    if directory:
        if verbose >= 1:
            dir_files = walk_dir_media(directory, silent=False)
        else:
            dir_files = walk_dir_media(directory)
        print(dir_files)

        for d in dir_files:
            p = pathlib.Path(d)
            if p.suffix in iops.IMAGE_EXTENSIONS:
                _cmd += f"magick convert {d} -resize {percentage}% {p.stem}_smaller{p.suffix}\n\n"
                if remove_old:
                    _cmd += f"rm -fv {d}\n\n"
            elif p.suffix in iops.VIDEO_EXTENSIONS:
                _cmd += f"""
                ffmpeg -y -hide_banner -loglevel warning -i \"{d}\" -vf "scale=128:128:force_original_aspect_ratio=decrease,pad=128:128:-1:-1:color=white,setdar=1:1" \"{p.stem}_smaller{p.suffix}\"
                """
                if remove_old:
                    _cmd += f"rm -fv {d}\n"

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    if print_only:
        rich.print("only running print")
    else:
        rich.print("executing ...")
        # ctx.run(_cmd)


@task(
    pre=[
        call(detect_os, loc="local"),
        call(clean, loc="local"),
        call(rsync, loc="local"),
    ],
    incrementable=["verbose"],
)
def dev(ctx, loc="local", verbose=0, cleanup=False):
    """
    install dev version of application
    Usage: inv local.dev
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = r"""
pip install -e .
    """

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)

    msg = "[dev] testing cli works"
    click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run("dancedetectorctl --help")


@task(
    pre=[
        call(detect_os, loc="local"),
        call(clean, loc="local"),
    ],
    incrementable=["verbose"],
)
def setup_jupyter(ctx, loc="local", verbose=0, cleanup=False):
    """
    Setup jupyter notebook
    Usage: inv local.setup-jupyter
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    msg = "[setup-jupyter] installing dependencies"
    click.secho(msg, fg=COLOR_SUCCESS)

    _cmd = r"""
pip install jupyter
pip install ipython-sql cython
python -m ipykernel install --user
pip install jupyter_nbextensions_configurator jupyter_contrib_nbextensions
jupyter contrib nbextension install --user
jupyter nbextensions_configurator enable --user
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension --sys-prefix
    """

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)


@task(
    pre=[
        call(detect_os, loc="local"),
        call(clean, loc="local"),
    ],
    incrementable=["verbose"],
)
def jupyter(ctx, loc="local", verbose=0, cleanup=False):
    """
    Run jupyter notebook
    Usage: inv local.jupyter
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    _cmd = r"""
pip install -e .
    """

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)

    msg = "[jupyter] start up notebook"
    click.secho(msg, fg=COLOR_SUCCESS)

    msg = (
        "[jupyter] Great guide to jupyter here: https://www.datacamp.com/community/tutorials/tutorial-jupyter-notebook"
    )
    click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run("jupyter notebook")


@task(
    pre=[
        call(detect_os, loc="local"),
        call(clean, loc="local"),
    ],
    incrementable=["verbose"],
)
def list_ports(ctx, loc="local", verbose=0, cleanup=False):
    """
    Run jupyter notebook
    Usage: inv local.list-ports
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    # SOURCE: https://wilsonmar.github.io/ports-open/
    # lsof -nP +c 15 | grep LISTEN
    _cmd = r"""
nmap -p 8000,3000,5678,6666 localhost
    """

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)


@task(
    pre=[
        call(detect_os, loc="local"),
        call(clean, loc="local"),
    ],
    incrementable=["verbose"],
)
def pstree(ctx, loc="local", verbose=0, cleanup=False):
    """
    Run jupyter notebook
    Usage: inv local.pstree
    """
    env = get_compose_env(ctx, loc=loc)

    # Override run commands' env variables one key at a time
    for k, v in env.items():
        ctx.config["run"]["env"][k] = v

    # SOURCE: https://wilsonmar.github.io/ports-open/
    # lsof -nP +c 15 | grep LISTEN
    _cmd = r"""
ps aux | grep 'python dancedetector/web.py' | awk '{print $2}' | head -1
    """

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    pid_res = ctx.run(_cmd)

    _cmd = r"""
pstree -p {}
    """.format(
        pid_res.stdout
    )

    if verbose >= 1:
        msg = f"{_cmd}"
        click.secho(msg, fg=COLOR_SUCCESS)

    ctx.run(_cmd)
