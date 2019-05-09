#! /bin/bash

echo $TRAVIS_OS_NAME

 if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then

    # Travis has an old version of pyenv by default, upgrade it
    brew update > /dev/null 2>&1
    brew outdated pyenv || brew upgrade pyenv

    pyenv --version

    # Find the latest requested version of python
    case "$TOXENV" in
        py34)
            python_minor=4;;
        py35)
            python_minor=5;;
        py36)
            python_minor=6;;
        py37)
            python_minor=7;;
    esac
    latest_version=`pyenv install --list | grep -e "^[ ]*3\.$python_minor" | tail -1`

    pyenv install $latest_version
    pyenv local $latest_version
fi
