#!/usr/bin/env bash

git push && git push --tags
rm dist/*.tar.gz
python setup.py sdist
twine upload dist/* --repository pypi

# Content of the .pypirc:
#
#  [distutils]
#    servers = pypi
#
#  [pypi]
#    username = __token__
#    password = ...
