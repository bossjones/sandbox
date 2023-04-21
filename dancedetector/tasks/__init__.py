# pylint: disable=wrong-import-position, wrong-import-order, invalid-name
"""
Invoke build script.
Show all tasks with::
    invoke -l
.. seealso::
    * http://pyinvoke.org
    * https://github.com/pyinvoke/invoke
"""
###############################################################################
# Catch exceptions and go into ipython/ipdb
# import sys

# from IPython.core.debugger import Tracer  # noqa
# from IPython.core import ultratb

# sys.excepthook = ultratb.FormattedTB(
#     mode="Verbose", color_scheme="Linux", call_pdb=True, ostream=sys.__stdout__
# )
###############################################################################


import logging
from invoke import Collection, Context, Config
from invoke import task
from .constants import ROOT_DIR, PROJECT_BIN_DIR, DATA_DIR, SCRIPT_DIR

# from . import core
from . import local

# from . import travis
from . import ci
from . import view

# from . import program
# from . import db
# from .git import pr_sha

LOGGER = logging.getLogger()

ns = Collection()
# ns.add_collection(core)
ns.add_collection(local)
# ns.add_collection(travis)
ns.add_collection(ci)
ns.add_collection(view)
# ns.add_collection(program)
# ns.add_collection(db)
# ns.add_collection(git)
# ns.add_task(pr_sha)

# https://github.com/imbrra/logowanie/blob/38a1a38ea9f5b2494e5bc986df651ff9d713fda5/tasks/__init__.py

# TODO: THINK ABOUT USING THESE MODULES https://medium.com/hultner/how-to-write-bash-scripts-in-python-10c34a5c2df1
# TODO: THINK ABOUT USING THESE MODULES https://medium.com/hultner/how-to-write-bash-scripts-in-python-10c34a5c2df1
# TODO: THINK ABOUT USING THESE MODULES https://medium.com/hultner/how-to-write-bash-scripts-in-python-10c34a5c2df1
