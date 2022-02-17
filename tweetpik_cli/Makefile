# -*- coding: utf-8 -*-
# SOURCE: https://github.com/autopilotpattern/jenkins/blob/master/makefile
MAKEFLAGS += --warn-undefined-variables
# .SHELLFLAGS := -eu -o pipefail

# SOURCE: https://github.com/luismayta/zsh-servers-functions/blob/b68f34e486d6c4a465703472e499b1c39fe4a26c/Makefile
# Configuration.
SHELL = /bin/bash
ROOT_DIR = $(shell pwd)
PROJECT_BIN_DIR = $(ROOT_DIR)/bin
DATA_DIR = $(ROOT_DIR)/var
SCRIPT_DIR = $(ROOT_DIR)/script

WGET = wget
# SOURCE: https://github.com/wk8838299/bullcoin/blob/8182e2f19c1f93c9578a2b66de6a9cce0506d1a7/LMN/src/makefile.osx
HAVE_BREW=$(shell brew --prefix >/dev/null 2>&1; echo $$? )


.PHONY: list help default all check fail-when-git-dirty
.PHONY: pre-commit-install check-connection-postgres monkeytype-stub monkeytype-apply monkeytype-ci

.PHONY: FORCE_MAKE

PR_SHA                := $(shell git rev-parse HEAD)

define ASCILOGO
tweetpik_cli
=======================================
endef

export ASCILOGO

# http://misc.flogisoft.com/bash/tip_colors_and_formatting

RED=\033[0;31m
GREEN=\033[0;32m
ORNG=\033[38;5;214m
BLUE=\033[38;5;81m
NC=\033[0m

export RED
export GREEN
export NC
export ORNG
export BLUE

# verify that certain variables have been defined off the bat
check_defined = \
		$(foreach 1,$1,$(__check_defined))
__check_defined = \
		$(if $(value $1),, \
			$(error Undefined $1$(if $(value 2), ($(strip $2)))))

export PATH := ./script:./bin:./bash:./venv/bin:$(PATH)

MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
CURRENT_FOLDER := $(notdir $(patsubst %/,%,$(dir $(MKFILE_PATH))))
CURRENT_DIR := $(shell pwd)
MAKE := make
PY_MODULE_NAME := tweetpik_cli

list_allowed_args := product ip command role tier cluster non_root_user host

default: all

all: info


#--- User Defined Variable ---
PACKAGE_NAME="tweetpik_cli"

# Python version Used for Development
PY_VER_MAJOR="3"
PY_VER_MINOR="9"
PY_VER_MICRO="5"

#  Other Python Version You Want to Test With
# (Only useful when you use tox locally)
TEST_PY_VER3="3.9.5"

# If you use pyenv-virtualenv, set to "Y"
USE_PYENV="Y"

# S3 Bucket Name
DOC_HOST_BUCKET_NAME="NoBucket"


#--- Derive Other Variable ---

# Virtualenv Name
VENV_NAME="${PACKAGE_NAME}${PY_VER_MAJOR}"

# Project Root Directory
GIT_ROOT_DIR=${shell git rev-parse --show-toplevel}
PROJECT_ROOT_DIR=${shell pwd}

OS=${shell uname -s}

ifeq (${OS}, Windows_NT)
		DETECTED_OS := Windows
else
		DETECTED_OS := $(shell uname -s)
endif


# ---------

# Windows
ifeq (${DETECTED_OS}, Windows)
		USE_PYENV="N"

		VENV_DIR_REAL="${PROJECT_ROOT_DIR}/${VENV_NAME}"
		BIN_DIR="${VENV_DIR_REAL}/Scripts"
		SITE_PACKAGES="${VENV_DIR_REAL}/Lib/site-packages"
		SITE_PACKAGES64="${VENV_DIR_REAL}/Lib64/site-packages"

		GLOBAL_PYTHON="/c/Python${PY_VER_MAJOR}${PY_VER_MINOR}/python.exe"
		OPEN_COMMAND="start"
endif


# MacOS
ifeq (${DETECTED_OS}, Darwin)

ifeq ($(USE_PYENV), "Y")
		ARCHFLAGS="-arch x86_64"
		PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig
		LDFLAGS="-L/usr/local/opt/openssl/lib"
		CFLAGS="-I/usr/local/opt/openssl/include"
		VENV_DIR_REAL="${HOME}/.pyenv/versions/${PY_VERSION}/envs/${VENV_NAME}"
		VENV_DIR_LINK="${HOME}/.pyenv/versions/${VENV_NAME}"
		BIN_DIR="${VENV_DIR_REAL}/bin"
		SITE_PACKAGES="${VENV_DIR_REAL}/lib/python${PY_VER_MAJOR}.${PY_VER_MINOR}/site-packages"
		SITE_PACKAGES64="${VENV_DIR_REAL}/lib64/python${PY_VER_MAJOR}.${PY_VER_MINOR}/site-packages"
else
		ARCHFLAGS="-arch x86_64"
		PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig
		LDFLAGS="-L/usr/local/opt/openssl/lib"
		CFLAGS="-I/usr/local/opt/openssl/include"
		# VENV_DIR_REAL="${PROJECT_ROOT_DIR}/${VENV_NAME}"
		# VENV_DIR_LINK="./${VENV_NAME}"
		VENV_DIR_REAL="${HOME}/.pyenv/versions/${PY_VERSION}/envs/${VENV_NAME}"
		VENV_DIR_LINK="${HOME}/.pyenv/versions/${VENV_NAME}"
		BIN_DIR="${VENV_DIR_REAL}/bin"
		SITE_PACKAGES="${VENV_DIR_REAL}/lib/python${PY_VER_MAJOR}.${PY_VER_MINOR}/site-packages"
		SITE_PACKAGES64="${VENV_DIR_REAL}/lib64/python${PY_VER_MAJOR}.${PY_VER_MINOR}/site-packages"
endif
		ARCHFLAGS="-arch x86_64"
		PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig
		LDFLAGS="-L/usr/local/opt/openssl/lib"
		CFLAGS="-I/usr/local/opt/openssl/include"

		GLOBAL_PYTHON="python${PY_VER_MAJOR}.${PY_VER_MINOR}"
		OPEN_COMMAND="open"
endif


# Linux
ifeq (${DETECTED_OS}, Linux)
		USE_PYENV="N"

		VENV_DIR_REAL="${PROJECT_ROOT_DIR}/${VENV_NAME}"
		VENV_DIR_LINK="${PROJECT_ROOT_DIR}/${VENV_NAME}"
		BIN_DIR="${VENV_DIR_REAL}/bin"
		SITE_PACKAGES="${VENV_DIR_REAL}/lib/python${PY_VER_MAJOR}.${PY_VER_MINOR}/site-packages"
		SITE_PACKAGES64="${VENV_DIR_REAL}/lib64/python${PY_VER_MAJOR}.${PY_VER_MINOR}/site-packages"

		GLOBAL_PYTHON="python${PY_VER_MAJOR}.${PY_VER_MINOR}"
		OPEN_COMMAND="open"
endif


BASH_PROFILE_FILE = "${HOME}/.bash_profile"

BIN_ACTIVATE="${BIN_DIR}/activate"
BIN_PYTHON="${BIN_DIR}/python"
BIN_PIP="${BIN_DIR}/pip"
BIN_ISORT="${BIN_DIR}/isort"
BIN_JINJA="${BIN_DIR}/jinja2"
BIN_SPHINX_START="${BIN_DIR}/sphinx-quickstart"
BIN_TWINE="${BIN_DIR}/twine"
BIN_TOX="${BIN_DIR}/tox"
BIN_JUPYTER="${BIN_DIR}/jupyter"
BIN_PYTEST="${BIN_DIR}/pytest"

RTD_DOC_URL="https://tweetpik_cli.readthedocs.io/index.html"


PY_VERSION="${PY_VER_MAJOR}.${PY_VER_MINOR}.${PY_VER_MICRO}"

.PHONY: help
help: ## ** Show this help message
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#--- Make Commands ---
.PHONY: info
info: ## ** Show information about python, pip in this environment
	@printf "Info:\n"
	@printf "=======================================\n"
	@printf "$$GREEN venv:$$NC                               ${VENV_DIR_REAL}\n"
	@printf "$$GREEN python executable:$$NC                  ${BIN_PYTHON}\n"
	@printf "$$GREEN pip executable:$$NC                     ${BIN_PIP}\n"
	@printf "$$GREEN site-packages:$$NC                      ${SITE_PACKAGES}\n"
	@printf "$$GREEN site-packages64:$$NC                    ${SITE_PACKAGES64}\n"
	@printf "$$GREEN venv-dir-real:$$NC                      ${VENV_DIR_REAL}\n"
	@printf "$$GREEN venv-dir-link:$$NC                      ${VENV_DIR_LINK}\n"
	@printf "$$GREEN venv-bin-dir:$$NC                       ${BIN_DIR}\n"
	@printf "$$GREEN bash-profile-file:$$NC                  ${BASH_PROFILE_FILE}\n"
	@printf "$$GREEN bash-activate:$$NC                      ${BIN_ACTIVATE}\n"
	@printf "$$GREEN bin-python:$$NC                         ${BIN_PYTHON}\n"
	@printf "$$GREEN bin-isort:$$NC                          ${BIN_ISORT}\n"
	@printf "$$GREEN py-version:$$NC                         ${PY_VERSION}\n"
	@printf "$$GREEN use-pyenv:$$NC                          ${USE_PYENV}\n"
	@printf "$$GREEN venv-name:$$NC                          ${VENV_NAME}\n"
	@printf "$$GREEN git-root-dir:$$NC                       ${GIT_ROOT_DIR}\n"
	@printf "$$GREEN project-root-dir:$$NC                   ${PROJECT_ROOT_DIR}\n"
	@printf "$$GREEN brew-is-installed:$$NC                  ${HAVE_BREW}\n"
	@printf "\n"

#--- Virtualenv ---
.PHONY: brew_install_pyenv
brew_install_pyenv: ## ** Install pyenv and pyenv-virtualenv
	-brew install pyenv
	-brew install pyenv-virtualenv

.PHONY: setup_pyenv
setup_pyenv: brew_install_pyenv enable_pyenv ## ** Do some pre-setup for pyenv and pyenv-virtualenv
	pyenv install ${PY_VERSION} -s
	pyenv rehash

.PHONY: bootstrap_venv
bootstrap_venv: pre_commit_install init_venv dev_dep show_venv_activate_cmd ## ** Create virtual environment, initialize it, install packages, and remind user to activate after make is done
# bootstrap_venv: init_venv dev_dep ## ** Create virtual environment, initialize it, install packages, and remind user to activate after make is done

.PHONY: bootstrap
bootstrap: pip-tools bootstrap_venv

.PHONY: init_venv
init_venv: ## ** Initiate Virtual Environment
ifeq (${USE_PYENV}, "Y")
ifneq ("$(wildcard $(VENV_DIR_REAL))","")
	@printf "=======================================\n"
	@printf "$$GREEN virtualenv alredy exists ${VENV_NAME}:$$NC\n"
	@printf "=======================================\n"
else
	@printf "=======================================\n"
	@printf "$$GREEN Creating virtualenv ${VENV_NAME}:$$NC\n"
	-pyenv virtualenv ${PY_VERSION} ${VENV_NAME}
	@printf "FINISHED:\n"
	@printf "=======================================\n"
	@printf "$$GREEN Run to activate virtualenv:$$NC                               pyenv activate ${VENV_NAME}\n"
	@printf "$$GREEN After you activate run the following:$$NC                               pyenv rehash\n"
	-pyenv rehash
endif

else

ifeq ($(HAVE_BREW), 0)
	DEPSDIR='ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include"'
	$(DEPSDIR) virtualenv -p ${GLOBAL_PYTHON} ${VENV_NAME}
endif

	virtualenv -p ${GLOBAL_PYTHON} ${VENV_NAME}
endif


.PHONY: up
up: init_venv ## ** Set Up the Virtual Environment


.PHONY: clean_venv
clean_venv: ## ** Clean Up Virtual Environment
ifeq (${USE_PYENV}, "Y")
	-pyenv uninstall -f ${VENV_NAME}
else
	test -r ${VENV_DIR_REAL} || echo "DIR exists: ${VENV_DIR_REAL}" || rm -rv ${VENV_DIR_REAL}
endif


#--- Install ---

.PHONY: uninstall
uninstall: ## ** Uninstall This Package
	# -${BIN_PIP} uninstall -y ${PACKAGE_NAME}
	-${BIN_PIP} uninstall -y requirements.txt

.PHONY: install
# install: uninstall ## ** Install This Package via setup.py
install: ## ** Install This Package via setup.py
ifeq ($(HAVE_BREW), 0)
	DEPSDIR='ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include"'
	$(DEPSDIR) ${BIN_PIP} install -r requirements.txt
else
	${BIN_PIP} install -r requirements.txt
endif


.PHONY: dev_dep
dev_dep: ## ** Install Development Dependencies

ifeq ($(HAVE_BREW), 0)
	( \
		cd ${PROJECT_ROOT_DIR}; \
		ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" ${BIN_PIP} install -r requirements.txt; \
		ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" ${BIN_PIP} install -r requirements-dev.txt; \
		ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" ${BIN_PIP} install -r requirements-doc.txt; \
		ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" ${BIN_PIP} install -r requirements-test.txt; \
	)
else
	( \
		cd ${PROJECT_ROOT_DIR}; \
		${BIN_PIP} install -r requirements.txt; \
		${BIN_PIP} install -r requirements-dev.txt; \
		${BIN_PIP} install -r requirements-test.txt; \
		${BIN_PIP} install -r requirements-doc.txt; \
	)
endif

.PHONY: install-dev
install-dev: dev_dep ## ** Install Development Dependencies


.PHONY: show_venv_activate_cmd
show_venv_activate_cmd: ## ** Show activate command when finished
	@printf "Don't forget to run this activate your new virtualenv:\n"
	@printf "=======================================\n"
	@echo
	@printf "$$GREEN pyenv activate $(VENV_NAME)$$NC\n"
	@echo
	@printf "=======================================\n"


###########################################################
# Pyenv initilization - 12/23/2018 -- END
# SOURCE: https://github.com/MacHu-GWU/learn_datasette-project/blob/120b45363aa63bdffe2f1933cf2d4e20bb6cbdb8/make/python_env.mk
###########################################################

.PHONY: list
list:
	@$(MAKE) -qp | awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}' | sort

# Compile python modules against homebrew openssl. The homebrew version provides a modern alternative to the one that comes packaged with OS X by default.
# OS X's older openssl version will fail against certain python modules, namely "cryptography"
# Taken from this git issue pyca/cryptography#2692
.PHONY: install-virtualenv-osx
install-virtualenv-osx:
	ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install -r requirements.txt

.PHONY: pre_commit_install
pre_commit_install: pre-commit-install
# -cp git_hooks/.pre-commit-config.yaml .git/hooks/pre-commit

.PHONY: run-black-check
run-black-check: ## CHECK MODE: sensible pylint ( Lots of press over this during pycon 2018 )
	black --check --exclude=tweetpik_cli_venv*,*.eggs --verbose .

.PHONY: run-black
run-black: ## sensible pylint ( Lots of press over this during pycon 2018 )
	black --verbose --exclude=tweetpik_cli_venv*,*.eggs .

.PHONY: pip-tools
pip-tools:
ifeq (${DETECTED_OS}, Darwin)
	ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install pip-tools pipdeptree
else
	pip install pip-tools pipdeptree
endif

.PHONY: pip-tools-osx
pip-tools-osx: pip-tools

.PHONY: pip-tools-upgrade
pip-tools-upgrade:
ifeq (${DETECTED_OS}, Darwin)
	ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install pip-tools pipdeptree --upgrade
else
	pip install pip-tools pipdeptree --upgrade
endif

.PHONY: pip-compile-upgrade-all
pip-compile-upgrade-all: pip-tools-upgrade
	pip-compile --output-file requirements.txt requirements.in --upgrade
	pip-compile --output-file requirements-dev.txt requirements-dev.in --upgrade
	pip-compile --output-file requirements-test.txt requirements-test.in --upgrade
	pip-compile --output-file requirements-doc.txt requirements-doc.in --upgrade
	pip-compile --output-file requirements-experimental.txt requirements-experimental.in --upgrade

.PHONY: pip-compile
pip-compile: pip-tools
	pip-compile --output-file requirements.txt requirements.in
	pip-compile --output-file requirements-dev.txt requirements-dev.in
	pip-compile --output-file requirements-test.txt requirements-test.in
	pip-compile --output-file requirements-doc.txt requirements-doc.in
	pip-compile --output-file requirements-experimental.txt requirements-experimental.in

.PHONY: pip-compile-rebuild
pip-compile-rebuild: pip-tools
	pip-compile --rebuild --output-file requirements.txt requirements.in
	pip-compile --rebuild --output-file requirements-dev.txt requirements-dev.in
	pip-compile --rebuild --output-file requirements-test.txt requirements-test.in
	pip-compile --rebuild --output-file requirements-doc.txt requirements-doc.in
	pip-compile --rebuild --output-file requirements-experimental.txt requirements-experimental.in

.PHONY: install-deps-all
install-deps-all:
ifeq (${DETECTED_OS}, Darwin)
	PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install -r requirements.txt
	PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install -r requirements-dev.txt
	PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install -r requirements-test.txt
	PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install -r requirements-doc.txt
	PKG_CONFIG_PATH=/usr/local/opt/libffi/lib/pkgconfig ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" pip install -r requirements-experimental.txt
else
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -r requirements-test.txt
	pip install -r requirements-doc.txt
	pip install -r requirements-experimental.txt
endif

.PHONY: pip-compile-and-install
pip-compile-and-install: pip-compile install-deps-all ## generate requirement.txt files, then install all of those dependencies

.PHONY: install-all
install-all: install-deps-all

.PHONY: yamllint-role
yamllint-role:
	bash -c "find .* -type f -name '*.y*ml' ! -name '*.venv' -print0 | xargs -I FILE -t -0 -n1 yamllint FILE"

.PHONY: install-ip-cmd-osx
install-ip-cmd-osx:
	brew install iproute2mac

.PHONY: flush-cache
flush-cache:
	@sudo killall -HUP mDNSResponder


###############################

# A Self-Documenting Makefile: http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.PHONY: git-clean git-env pipenv-test pipenv-test-cover pipenv-test-cli help2

.PHONY: git-clean
git-clean: ## Remove files and directories ignored by git
	git clean -d -X -f

install-nltk-data:
	python -m nltk.downloader popular


pre-commit-install: ## install all pre-commit hooks
	pre-commit install -f --install-hooks

check-connection-postgres:
	./scripts/check_connection.py

monkeytype-stub:
	inv ci.monkeytype -vvvv --test --stub

monkeytype-apply:
	inv ci.monkeytype -vvvv --test --apply

monkeytype-ci: monkeytype-stub monkeytype-apply

example-repos:
	git clone https://github.com/jwlodek/pyautogit ~/dev/pyautogit || true
	git clone https://github.com/jwlodek/py_cui ~/dev/py_cui || true
	git clone https://github.com/ckardaris/ucollage ~/dev/ucollage || true
	git clone https://github.com/peterbrittain/asciimatics ~/dev/asciimatics || true
	git clone https://github.com/seebye/ueberzug ~/dev/ueberzug || true

	mkdir -p ~/dev/python-gui-examples/ || true
	git clone https://github.com/trin5tensa/moviedb ~/dev/python-gui-examples/moviedb || true
	git clone https://github.com/Zvosab/image_to_png ~/dev/python-gui-examples/image_to_png || true
	git clone https://github.com/Sawera557/Find-Exif-Data ~/dev/python-gui-examples/Find-Exif-Data || true
	git clone https://github.com/mutomasa/small-image-viewer ~/dev/python-gui-examples/small-image-viewer || true
	git clone https://github.com/rmartm14/ImageView ~/dev/python-gui-examples/ImageView || true
	git clone https://github.com/nngogol/async-desktop-chat ~/dev/python-gui-examples/async-desktop-chat || true
	git clone https://github.com/XavierTheCreator/YTDownloader ~/dev/python-gui-examples/YTDownloader || true
	git clone https://github.com/john144/MultiThreading ~/dev/python-gui-examples/MultiThreading || true
	git clone https://github.com/PySimpleGUI/PySimpleGUI-Photo-Colorizer ~/dev/python-gui-examples/PySimpleGUI-Photo-Colorizer || true
	git clone https://github.com/PabloLec/pyautogit ~/dev/python-gui-examples/pyautogit || true
	git clone https://github.com/jupiterbjy/CUIAudioPlayer ~/dev/python-gui-examples/CUIAudioPlayer || true
	git clone https://github.com/HakierGrzonzo/tinyPub ~/dev/python-gui-examples/tinyPub || true
	git clone https://github.com/channel-42/hue-tui ~/dev/python-gui-examples/hue-tui || true
	git clone https://github.com/wdog/mini-radio-player-pycui ~/dev/python-gui-examples/mini-radio-player-pycui || true

install-editable:
	pip install -e .

pip-sync: pip-compile install-deps-all install-editable
	pip-sync requirements.txt requirements-dev.txt requirements-doc.txt requirements-experimental.txt requirements-test.txt


.PHONY: setup-feature-flags
setup-feature-flags:
	scripts/init-feature-flags.sh

.PHONY: reset-dev-env
reset-dev-env: pip-compile pip-sync install-deps-all install-editable


.PHONY: log
log:
	tail -f tui.log | ccze -A

.PHONY: folders
folders:
	scripts/folders.sh

# SOURCE: https://queirozf.com/entries/jupyter-kernels-how-to-add-change-remove
.PHONY: setup-jupyter-kernel
setup-jupyter-kernel:
	ipython kernel install --name="${VENV_NAME}" --user
# Installed kernelspec tweetpik_cli3 in /Users/malcolm/Library/Jupyter/kernels/tweetpik_cli3
# python -m ipykernel install --user --name=tweetpik_cli3
.PHONY: install-opencv-typing
install-opencv-typing:
# curl -sSL https://raw.githubusercontent.com/bossjones/python-type-stubs/add-opencv/cv2/__init__.pyi -o $(python -c 'import cv2, os; print(os.path.dirname(cv2.__file__))')/cv2.pyi
	./contrib/install_opencv_typing.sh

jupyter-notebook:
	jupyter notebook --port=2375 --ip=0.0.0.0

editable-install:
	pip install -e .[dev,tests,experimental,docs]

dev: pip-compile install-deps-all editable-install install-opencv-typing

predict_smoke_test:
	curl \
	-X POST \
	"http://localhost:11267/predict/image" \
	-H "accept: application/json" \
	-H "Content-Type: multipart/form-data" \
	-F "filecomment=This is an image file" \
	-F "file=@$(PWD)/images/beach.png;type=image/png"

dropbox_smoke_test:
	curl \
	-X POST \
	"http://localhost:11267/dropbox/upload" \
	-H "accept: application/json" \
	-H "Content-Type: multipart/form-data" \
	-F "filecomment=This is an image file" \
	-F "file=@$(PWD)/images/beach.png;type=image/png"
