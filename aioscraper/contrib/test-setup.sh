#shellcheck shell=bash source=/dev/null
# SOURCE: https://github.com/markfaine/new_project_files/blob/f99138e4dd09234531079c96dad59fadff768b44/test-setup.sh

# function: debug: print debug messages
function debug() {
  if [[ $DEBUG == 'true' ]]; then
    echo -e "\e[31mDEBUG: ==> $*\e[0m";
  fi
}

# function: e: print debug messages
function e() { echo -e "\e[32m$*\e[0m"; }

# function: _install_os_deps: installs operating system package dependencies
function _install_os_deps(){
  e "Installing OS dependencies..."
  packages=(make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev
            libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
            xz-utils tk-dev libffi-dev liblzma-dev python-openssl git)
  for package in "${packages[@]}"; do
    debug "$package is already installed"
    if ! dpkg-query -s "${package}" >/dev/null 2>&1; then
      debug "Attempting to install $package"
      if sudo apt-get -y install "${package}" >/dev/null 2>&1; then
        debug "$package successfull installed"
      else
        debug "$package was not installed!"
      fi
    fi
  done
  e "Success"
}

# function: _install_pyenv: installs python version manager
function _install_pyenv() {
  if [[ -d ~/.pyenv ]]; then
    debug "$HOME/.pyenv already exists"
    return
  else
    e "Installing pyenv and dependencies..."
    e "This process should only occur once unless ~/.pyenv is deleted"
    if git clone https://github.com/pyenv/pyenv.git "$HOME/.pyenv" >/dev/null 2>&1; then
      e "Success"
    else
      debug "Failed to install pyenv!"
      return $?
    fi
  fi
}

# function: _install_pyenv-default-packages: installs plugin to install default packages automatically
function _install_pyenv-default-packages(){
  if [[ -d "${PYENV_ROOT}/plugins/pyenv-default-packages" ]]; then
    debug "${PYENV_ROOT}/plugins/pyenv-default-packages already exists"
    return
  else
    e "Installing pyenv-default-packages plugin..."
    e "This process should only occur once unless ~/.pyenv/plugins/pyenv-default-packages is deleted"
    # Install pyenv virtualenvwrapper plugin
    if git clone https://github.com/jawshooah/pyenv-default-packages.git "$HOME/.pyenv/plugins/pyenv-default-packages" >/dev/null 2>&1; then
      PATH="$PATH:${PYENV_ROOT}/plugins/pyenv-default-packages/libexec"; export PATH
      cat <<- EOF > "$(pyenv root)/default-packages"
			ansible==2.7.9
			ansible-lint<5,>=4.0.2
			pycodestyle<2.6.0,>=2.5.0
			autopep8==1.4
			flake8<4,>=3.6.0
			six==1.11.0
			python-vagrant
			pre-commit
			ansible-lint>=4.0.2,<5
			anyconfig==0.9.7
			cerberus==1.2
			click==6.7
			click-completion==0.3.1
			colorama==0.3.9
			cookiecutter==1.6.0
			cryptography
			idna<2.8  # because indirect dependency "requests" conflict with it now
			python-gilt==1.2.1
			Jinja2==2.10
			pbr==5.1.1
			pexpect==4.6.0
			psutil==5.4.6; sys_platform!="win32" and sys_platform!="cygwin"
			pywinrm[kerberos]>=0.3.0
			PyYAML==3.13
			sh==1.12.14
			six==1.11.0
			tabulate==0.8.2
			testinfra==1.19.0
			tree-format==0.1.2
			molecule
			EOF
      e "Success"
    else
      debug "Could not install pyenv-default-packages!"
    fi
  fi
}

# function: _install_python
function _install_python() {
  # Install python 3.9.0 if not already installed, python is needed for virtualenvwraper
  _install_os_deps
  if [[ -d "$HOME/.pyenv/versions/3.9.0" ]] ; then
    debug "Python version is already installed"
    return
  else
    e "Installing python 3.9.0into ${PYENV_ROOT}/versions"
    CFLAGS='-O2'; export CFLAGS
    if ! pyenv install 3.9.0>/dev/null 2>&1; then
      debug "Could not install python!"
      return $?
    fi
  fi
}

# function: _install_pyenv_wrapper: installs plugin to combine pyenv and virtualenvwrapper functions
function _install_pyenv_wrapper(){
  if [[ -d "${PYENV_ROOT}/plugins/pyenv-virtualenvwrapper" ]]; then
    debug "pyenv-virtualenvwrapper is already installed"
    return
  else
    e "Installing pyenv-virtualenvwrapper plugin..."
    e "This process should only occur once unless ~/.pyenv/plugins/pyenv-virtualenvwrapper is deleted"
    # Install pyenv virtualenvwrapper plugin
    if git clone https://github.com/pyenv/pyenv-virtualenvwrapper.git "$HOME/.pyenv/plugins/pyenv-virtualenvwrapper" >/dev/null 2>&1; then
      PATH="$PATH:${PYENV_ROOT}/plugins/pyenv-virtualenvwrapper/bin"; export PATH
      e "Success"
    else
      debug "Failed to install pyenv-virtualenvwrapper!"
      return $?
    fi
  fi
}

#function: virtualenvwrapper: setup virtualenvwrapper
function _pyenv_virtualenvwrapper() {
  if [[ ! -d "${PYENV_ROOT}/plugins/pyenv-virtualenvwrapper" ]]; then
    debug "pyenv-virtualenvwrapper is not installed!"
    return
  else
    WORKON_HOME=~/.virtualenvs; export VIRTUALENVWRAPPER_VIRTUALENV_ARGS
    PROJECT_HOME=~/projects; export PROJECT_HOME
    VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'; export WORKON_HOME
    mkdir -p "${WORKON_HOME}"
    mkdir -p "${PROJECT_HOME}"
    pyenv virtualenvwrapper >/dev/null 2>&1;
  fi
}


#function: update_bashrc:  Add necessary source calls to .bashrc
function update_bashrc(){
  e "Updating $HOME/.bashrc"
  sed  -i '/##START-ANSIBLE-TEST##/,/##END-ANSIBLE-TEST##/d' "$HOME/.bashrc"
  cat <<- EOF >> "$HOME/.bashrc"
##START-ANSIBLE-TEST##
## Added by $0 on $(date)
if [[ -e "\$HOME/.pyenv_config" ]]; then
  source "\$HOME/.pyenv_config"
fi
##END-ANSIBLE-TEST##
	EOF
e "Success"
}

#function: create_config:  Install a configuraiton file in the user's home directory.  It will be sourced at login
function create_config(){
  e "Creating config file $HOME/.pyenv_config"
  cat <<- EOF > "$HOME/.pyenv_config"
PYENV_ROOT="\$HOME/.pyenv"; export PYENV_ROOT
PATH="\${PYENV_ROOT}/bin:\$PATH"
# Enable shims and autocompletion
eval "\$(pyenv init -)" || return
# Enable pyenv
WORKON_HOME="\$HOME/.virtualenvs"; export VIRTUALENVWRAPPER_VIRTUALENV_ARGS
PROJECT_HOME="\$HOME/projects"; export PROJECT_HOME
VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'; export WORKON_HOME
mkdir -p "\${WORKON_HOME}"
mkdir -p "\${PROJECT_HOME}"
pyenv virtualenvwrapper >/dev/null 2>&1
EOF
if [[ $(uname -a) =~ Microsoft ]]; then
  echo "VAGRANT_WSL_ENABLE_WINDOWS_ACCESS=\"1\";export VAGRANT_WSL_ENABLE_WINDOWS_ACCESS" >> "$HOME/.pyenv_config"
  echo "PATH=\"\$PATH:/mnt/c/Program Files/Oracle/VirtualBox\";export PATH" >> "$HOME/.pyenv_config"
fi
e "Success"
}

cat << EOF
This script is intended for Ubuntu or Ubuntu under WSL
It will install the necessary system dependencies to test Ansible roles in a virtual environment using Molecule.
EOF

read -n1 -r -p "Press any key to continue..."


# Install pyenv
_install_pyenv
PYENV_ROOT="$HOME/.pyenv"; export PYENV_ROOT
PATH="${PYENV_ROOT}/bin:$PATH"; export PATH

# Enable shims and autocompletion
eval "$(pyenv init -)"

# Install plugins for pyenv
_install_pyenv-default-packages
_install_pyenv_wrapper

# Install python
_install_python
pyenv global 3.9.0>/dev/null 2>&1 # set default python installation
pyenv shell 3.9.0>/dev/null 2>&1 # set shell python version

# Upgrade pip
pip install --upgrade pip

create_config
update_bashrc

e "Sourcing $HOME/.bashrc"
source "$HOME/.bashrc"

cat <<- EOF
	This script only needs to be run once
  To create a virtualenv type:
  $ mkvirtualenv <name>
  For example,
  $ mkvirtualenv ansible
	To work in a virtualenv, type:
  $ workon <name>
  To exit a virtualenv just type:
  $ deactivate  (or exit the shell)
  Testing is performed with the molecule command, for more information type:
  $ molecule --help
  Ansible $(ansible --version | head -n 1 | awk '{ print $2 }') is available on the path as $(command -v ansible)
EOF
