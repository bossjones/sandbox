#!/usr/bin/env bash

# https://www.pyimagesearch.com/2019/12/09/how-to-install-tensorflow-2-0-on-macos/
brew install cmake pkg-config wget
brew install jpeg libpng libtiff openexr
brew install eigen tbb hdf5

# pytorch
brew install openblas
brew install libomp
brew install openmpi

# SOURCE: https://github.com/jiansoung/issues-list/issues/13
# Fixes: zipimport.ZipImportError: can't decompress data; zlib not available
export PATH="/usr/local/opt/tcl-tk/bin:$PATH"
export PATH="/usr/local/opt/bzip2/bin:$PATH"
export PATH="/usr/local/opt/ncurses/bin:$PATH"
export PATH="/usr/local/opt/openssl@1.1/bin:$PATH"
# SOURCE: https://github.com/jiansoung/issues-list/issues/13
# Fixes: zipimport.ZipImportError: can't decompress data; zlib not available
export LDFLAGS="${LDFLAGS} -L/usr/local/opt/openblas/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/openblas/include"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/openblas/lib/pkgconfig"

export LDFLAGS="${LDFLAGS} -L/usr/local/opt/tcl-tk/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/tcl-tk/include"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/tcl-tk/lib/pkgconfig"


export LDFLAGS="${LDFLAGS} -L/usr/local/opt/tcl-tk/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/tcl-tk/include"
export LDFLAGS="${LDFLAGS} -L/usr/local/opt/zlib/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/zlib/include"
export LDFLAGS="${LDFLAGS} -L/usr/local/opt/sqlite/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/sqlite/include"
export LDFLAGS="${LDFLAGS} -L/usr/local/opt/libffi/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/libffi/include"
export LDFLAGS="${LDFLAGS} -L/usr/local/opt/bzip2/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/bzip2/include"
export LDFLAGS="${LDFLAGS} -L/usr/local/opt/ncurses/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/ncurses/include"
export LDFLAGS="${LDFLAGS} -L/usr/local/opt/openssl@1.1/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/openssl@1.1/include"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/zlib/lib/pkgconfig"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/sqlite/lib/pkgconfig"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/tcl-tk/lib/pkgconfig"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/libffi/lib/pkgconfig"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/ncurses/lib/pkgconfig"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/openssl@1.1/lib/pkgconfig"
export PROFILE_TASK='-m test.regrtest --pgo \
    test_array \
    test_base64 \
    test_binascii \
    test_binhex \
    test_binop \
    test_bytes \
    test_c_locale_coercion \
    test_class \
    test_cmath \
    test_codecs \
    test_compile \
    test_complex \
    test_csv \
    test_decimal \
    test_dict \
    test_float \
    test_fstring \
    test_hashlib \
    test_io \
    test_iter \
    test_json \
    test_long \
    test_math \
    test_memoryview \
    test_pickle \
    test_re \
    test_set \
    test_slice \
    test_struct \
    test_threading \
    test_time \
    test_traceback \
    test_unicode \
'

echo "----------------------"
echo "Verify pyenv compile env vars"
echo "----------------------"
echo "LDFLAGS: ${LDFLAGS}"
echo "CPPFLAGS: ${CPPFLAGS}"
echo "PKG_CONFIG_PATH: ${PKG_CONFIG_PATH}"
echo "----------------------"

# env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.9.0
# SOURCE: https://www.kaggle.com/danofer/image-processing-and-sentiment-analysis
# pyenv virtualenv 3.9.0 tweetpik_cli3
# pyenv activate tweetpik_cli3
# pip install -U pip
# pip install pip-tools pipdeptree --upgrade
# pip install scipy pillow
# pip install imutils h5py requests progressbar2
# pip install scikit-learn scikit-image
# pip install matplotlib
# mkdir ~/.matplotlib
# touch ~/.matplotlib/matplotlibrc
# echo "backend: TkAgg" >> ~/.matplotlib/matplotlibrc
# pip install tensorflow
# pip install keras
# python -c "import keras;"
# pip install scenedetect[opencv]
# pip install seaborn
# pip install statsmodels
# pip install fastcluster
# pip install Pillow

# #### JUPYTER
# pip install jupyter
# pip install ipython-sql cython
# python -m ipykernel install
# # https://www.datacamp.com/community/tutorials/tutorial-jupyter-notebook
# # SOURCE: https://ndres.me/post/best-jupyter-notebook-extensions/
# pip install jupyter_nbextensions_configurator jupyter_contrib_nbextensions
# jupyter contrib nbextension install
# jupyter nbextensions_configurator enable
# # SOURCE: https://ipywidgets.readthedocs.io/en/latest/user_install.html
# pip install ipywidgets
# jupyter nbextension enable --py widgetsnbextension --sys-prefix
