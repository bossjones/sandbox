"""
Decides if vendor bundles are used or not.
Setup python path accordingly.
"""

import os.path
import sys

# -----------------------------------------------------------------------------
# DEFINES:
# -----------------------------------------------------------------------------
HERE = os.path.dirname(__file__)
# TASKS_VENDOR_DIR = os.path.join(HERE, "_vendor")
# INVOKE_BUNDLE = os.path.join(TASKS_VENDOR_DIR, "invoke.zip")
# INVOKE_BUNDLE_VERSION = "0.13.0"

# DEBUG_SYSPATH = False


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def setup_path_for_bundle(bundle_path, pos=0):
    if os.path.exists(bundle_path):
        syspath_insert(pos, os.path.abspath(bundle_path))
        return True
    return False


def syspath_insert(pos, path):
    if path in sys.path:
        sys.path.remove(path)
    sys.path.insert(pos, path)


def syspath_append(path):
    if path in sys.path:
        sys.path.remove(path)
    sys.path.append(path)
