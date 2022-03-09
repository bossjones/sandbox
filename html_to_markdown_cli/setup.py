"""
The setup script is the centre of all activity in building, distributing,
and installing modules using the Distutils. It is required for ``pip install``.
See more: https://docs.python.org/2/distutils/setupscript.html
"""


import os
import pprint
import sys
from datetime import date
from shutil import rmtree

from setuptools import Command
from setuptools import find_packages
from setuptools import setup

from urllib.parse import urlparse, urlunparse
from pathlib import PosixPath

import html_to_markdown_cli as package

# --- import your package ---

pp = pprint.PrettyPrinter(indent=4)

# https://github.com/GantMan/nsfw_model/tarball/master#egg=nsfw-detector

# SOURCE: https://github.com/yardstick17/AspectBasedSentimentAnalysis/blob/b1fcf830341a51f37a862b1144797d2a9c5db2c2/setup.py


def gh(name, version):
    package = name.split('/')[1]
    if 'GHE_ACCESS_TOKEN' in os.environ:
        proto = 'git+https://{}@'.format(os.environ['GHE_ACCESS_TOKEN'])
    elif 'CDP_BUILD_VERSION' in os.environ:
        proto = 'git+https://'
    else:
        proto = 'git+ssh://git@'
    return '{proto}github.com/{name}.git@{version}' \
        '#egg={package}-{version}'.format(**locals())

here = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":  # noqa: C901

    # --- Automatically generate setup parameters ---
    # Your package name
    PKG_NAME = package.__name__

    # Your GitHub user name
    try:
        GITHUB_USERNAME = package.__github_username__
    except:  # noqa: E722
        GITHUB_USERNAME = "Unknown-Github-Username"

    # Short description will be the description on PyPI
    try:
        SHORT_DESCRIPTION = package.__short_description__  # GitHub Short Description
    except:  # noqa: E722
        print("'__short_description__' not found in '%s.__init__.py'!" % PKG_NAME)
        SHORT_DESCRIPTION = "No short description!"

    # Long description will be the body of content on PyPI page
    try:
        LONG_DESCRIPTION = open("README.rst", "rb").read().decode("utf-8")
    except:  # noqa: E722
        LONG_DESCRIPTION = "No long description!"

    # Version number, VERY IMPORTANT!
    VERSION = package.__version__

    # Author and Maintainer
    try:
        AUTHOR = package.__author__
    except:  # noqa: E722
        AUTHOR = "Unknown"

    try:
        AUTHOR_EMAIL = package.__author_email__
    except:  # noqa: E722
        AUTHOR_EMAIL = None

    try:
        MAINTAINER = package.__maintainer__
    except:  # noqa: E722
        MAINTAINER = "Unknown"

    try:
        MAINTAINER_EMAIL = package.__maintainer_email__
    except:  # noqa: E722
        MAINTAINER_EMAIL = None

    PACKAGES, INCLUDE_PACKAGE_DATA, PACKAGE_DATA, PY_MODULES = (None, None, None, None)

    # It's a directory style package
    if os.path.exists(__file__[:-8] + PKG_NAME):
        # Include all sub packages in package directory
        PACKAGES = [PKG_NAME] + [
            "%s.%s" % (PKG_NAME, i) for i in find_packages(PKG_NAME)
        ]

        # Include everything in package directory
        INCLUDE_PACKAGE_DATA = True
        PACKAGE_DATA = {"": ["*.*"]}

    # It's a single script style package
    elif os.path.exists(__file__[:-8] + PKG_NAME + ".py"):
        PY_MODULES = [PKG_NAME]

    # The project directory name is the GitHub repository name
    repository_name = os.path.basename(os.path.dirname(__file__))

    # Project Url
    URL = "https://github.com/{0}/{1}".format(GITHUB_USERNAME, repository_name)

    # Use todays date as GitHub release tag
    github_release_tag = str(date.today())

    # Source code download url
    DOWNLOAD_URL = "https://pypi.python.org/pypi/{0}/{1}#downloads".format(
        PKG_NAME, VERSION
    )

    try:
        LICENSE = package.__license__
    except:  # noqa: E722
        print("'__license__' not found in '%s.__init__.py'!" % PKG_NAME)
        LICENSE = ""

    PLATFORMS = ["Windows", "MacOS", "Unix"]

    CLASSIFIERS = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ]
    """
    Full list can be found at: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    """

    def read_requirements_file(path, removes_links=True):
        """
        Read requirements.txt, ignore comments
        """
        requires = list()
        f = open(path, "rb")
        for line in f.read().decode("utf-8").split("\n"):
            line = line.strip()
            if "#" in line:
                line = line[: line.find("#")].strip()
            # skip if we are installing via scm repository
            if "-e git+https" in line:
                print("BAD LINE: {}".format(line))
                continue
            if "https:" in line and "tarball" in line:

                uri = urlparse(line)

                if "egg=" in uri.fragment:
                    fragment_split = uri.fragment.split('=')
                    dependency_name = fragment_split[1]
                else:
                    fragment_split = uri.fragment.split('=')
                    dependency_name = fragment_split[2]

                path_split = uri.path.split('/')
                line = f"{dependency_name} @ git+{uri.scheme}://{uri.netloc}/{path_split[1]}/{path_split[2]}@{path_split[4]}#egg={dependency_name}"
                print(line)

            if line:
                requires.append(line)
        return requires

    try:
        REQUIRES = read_requirements_file("requirements.txt")
    except:  # noqa: E722
        print("'requirements.txt' not found!")
        REQUIRES = list()

    EXTRA_REQUIRE = dict()

    try:
        EXTRA_REQUIRE["dev"] = read_requirements_file("requirements-dev.txt")
    except:  # noqa: E722
        print("'requirements-dev.txt' not found!")

    try:
        EXTRA_REQUIRE["tests"] = read_requirements_file("requirements-test.txt")
    except:  # noqa: E722
        print("'requirements-test.txt' not found!")

    try:
        EXTRA_REQUIRE["docs"] = read_requirements_file("requirements-doc.txt")
    except:  # noqa: E722
        print("'requirements-doc.txt' not found!")

    # import pdb;pdb.set_trace()

    try:
        EXTRA_REQUIRE["experimental"] = read_requirements_file(
            "requirements-experimental.txt"
        )
    except:  # noqa: E722
        print("'requirements-experimental.txt' not found!")

    TESTS_REQUIRE = dict()

    try:
        TESTS_REQUIRE = read_requirements_file("requirements-test.txt")
    except:  # noqa: E722
        print("'requirements-test.txt' not found!")

    class UploadCommand(Command):
        """Support setup.py upload."""

        description = "Build and publish the package."
        user_options = []

        @staticmethod
        def status(s):
            """Prints things in bold."""
            print("\033[1m{0}\033[0m".format(s))

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            try:
                self.status("Removing previous builds…")
                rmtree(os.path.join(here, "dist"))
            except OSError:
                pass

            self.status("Building Source and Wheel (universal) distribution…")
            os.system(
                "{0} setup.py sdist bdist_wheel --universal".format(sys.executable)
            )

            self.status("Uploading the package to PyPI via Twine…")
            os.system("twine upload dist/*")

            self.status("Pushing git tags…")
            os.system("git tag v{0}".format(VERSION))
            os.system("git push --tags")

            sys.exit()

    if sys.argv[-1] == "info":
        print("name=" + PKG_NAME)
        print("description=" + SHORT_DESCRIPTION)
        print("long_description=" + LONG_DESCRIPTION)
        print("version=" + VERSION)
        print("author=" + AUTHOR)
        print("author_email=" + AUTHOR_EMAIL)
        print("maintainer=" + MAINTAINER)
        print("maintainer_email=" + MAINTAINER_EMAIL)
        print("packages=" + pp.pprint(PACKAGES))
        print("setup_requires=" + ["pytest-runner"])
        print("tests_require=" + pp.pprint(TESTS_REQUIRE))
        print("include_package_data=" + INCLUDE_PACKAGE_DATA)
        print("package_data=" + PACKAGE_DATA)
        print("py_modules=" + PY_MODULES)
        print("url=" + URL)
        print("download_url=" + DOWNLOAD_URL)
        print("classifiers=" + CLASSIFIERS)
        print("platforms=" + PLATFORMS)
        print("license=" + LICENSE)
        print("install_requires=" + pp.pprint(REQUIRES))
        print("extras_require=" + pp.pprint(EXTRA_REQUIRE))
        sys.exit()

    setup(
        name=PKG_NAME,
        description=SHORT_DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        packages=PACKAGES,
        setup_requires=["pytest-runner"],
        tests_require=TESTS_REQUIRE,
        include_package_data=INCLUDE_PACKAGE_DATA,
        package_data=PACKAGE_DATA,
        py_modules=PY_MODULES,
        url=URL,
        download_url=DOWNLOAD_URL,
        classifiers=CLASSIFIERS,
        platforms=PLATFORMS,
        license=LICENSE,
        install_requires=REQUIRES,
        extras_require=EXTRA_REQUIRE,
        entry_points="""
        [console_scripts]
        html_to_markdown_cli=html_to_markdown_cli.cli:run
        """,
    )

"""
Appendix
--------
::

Frequent used classifiers List = [
    "Development Status :: 1 - Planning",
    "Development Status :: 2 - Pre-Alpha",
    "Development Status :: 3 - Alpha",
    "Development Status :: 4 - Beta",
    "Development Status :: 5 - Production/Stable",
    "Development Status :: 6 - Mature",
    "Development Status :: 7 - Inactive",

    "Intended Audience :: Customer Service",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Financial and Insurance Industry",
    "Intended Audience :: Healthcare Industry",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Legal Industry",
    "Intended Audience :: Manufacturing",
    "Intended Audience :: Other Audience",
    "Intended Audience :: Religion",
    "Intended Audience :: Science/Research",
    "Intended Audience :: System Administrators",
    "Intended Audience :: Telecommunications Industry",

    "License :: OSI Approved :: BSD License",
    "License :: OSI Approved :: MIT License",
    "License :: OSI Approved :: Apache Software License",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",

    "Natural Language :: English",
    "Natural Language :: Chinese (Simplified)",

    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "Operating System :: Unix",

    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3 :: Only",
]
"""
