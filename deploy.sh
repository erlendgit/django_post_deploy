#!/usr/bin/env bash

rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install twine setuptools

git push && git push --tags
rm dist/*.tar.gz
python setup.py sdist
twine upload dist/* --repository pypi

# Content of the .pypirc:
#
#  # is `distutils` niet gek? Maakt niet uit
#  # dat we eigenlijk setuptools gebruiken.
#  # Het werkt toch op deze manier.
#  [distutils]
#    servers = pypi
#
#  [pypi]
#    # Letterlijk: __token__
#    username = __token__
#    # De puntjes vervangen door je token.
#    password = ...
