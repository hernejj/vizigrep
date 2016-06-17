#!/usr/bin/env bash

echo "[pep8]"
pep8 --ignore W191,W293,E125,E201,E202,E221,E241,E261,E272,E302,E401,E501,E701 --exclude="./ut/test-data" ./

echo '[pyflakes]'
pyflakes *.py guiapp/*.py ut/*.py

echo '[desktop-file-validate]'
desktop-file-validate *.desktop
