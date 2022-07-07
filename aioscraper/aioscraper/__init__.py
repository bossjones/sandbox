"""aioscraper

Author: bossjones
Created:
"""
from pathlib import Path

__version__ = "0.0.1"
__short_description__ = "async dropbox client"
__license__ = "Apache 2.0"
__author__ = "@bossjones"
__author_email__ = "bossjones@theblacktonystark.com"
__maintainer__ = "@bossjones"
__maintainer_email__ = "jarvis@theblacktonystark.com"
__github_username__ = "bossjones"
__copyright__ = "2020-2021"
__repo_name__ = "https://github.com/bossjones/sandbox"

# https://dev.to/attakei/create-errbot-backend-storage-plugin-as-pypi-package-cc6
def get_plugin_dir() -> str:
    module_dir = Path(__file__).parent
    return str(module_dir)
