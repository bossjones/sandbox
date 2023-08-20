# dancedetector
Showing my work for Dr. Adrian Rosebrock's awesome book on computer vision


# v3 setup

```
# install just (Justfile)

pyenv virtualenv 3.9.10 dancedetector3

pyenv activate dancedetector3

just syncenv

just editable-install

pyenv rehash

dancedetectorctl doctor
```
