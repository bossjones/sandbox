#!/usr/bin/env bash

brew update

brew install cmake || true  # macos image has cmake installed, but a new version may exist; ignore it if so
brew install doxygen || true
brew install hdf5 || true
brew install pkg-config || true
brew install wget || true
brew install jpeg || true
brew install libpng || true
brew install libtiff || true
brew install openexr || true
brew install eigen || true
brew install tbb || true
brew install hdf5 || true

# pytorch
brew install openblas || true
brew install libomp || true
brew install openmpi || true
brew install tcl-tk || true

brew install openssl || true
brew install readline || true
brew install sqlite3 || true
brew install xz || true
brew install zlib || true

# https://techblog.willshouse.com/2013/05/20/brew-install-gnu-stat/
brew install coreutils || true
brew install findutils || true
brew install gnu-tar || true
brew install gnu-sed || true
brew install gawk || true
brew install gnutls || true
brew install gnu-getopt || true
brew install libmagic || true
brew install libffi || true
brew install atomicparsley || true
brew install tree || true
brew install tesseract || true

# https://github.com/jiaaro/pydub#installation
# libav
brew install libav || true

####    OR    #####

# ffmpeg
brew install ffmpeg || true
brew install meilisearch || true
