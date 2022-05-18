#!/usr/bin/env bash

git push && git push --tags
rm dist/*.tar.gz
python setup.py sdist
twine upload dist/* --repository django_post_deploy