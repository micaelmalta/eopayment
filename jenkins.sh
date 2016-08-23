#!/bin/sh

set -e

pip install --upgrade pip
pip install --upgrade pylint pylint-django
pip install --upgrade tox
(pylint -f parseable --rcfile /var/lib/jenkins/pylint.django.rc eopayment | tee pylint.out) || /bin/true
tox -r
