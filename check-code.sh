#!/usr/bin/env bash

echo "[pep8]"
pep8 --ignore W191 --exclude="./ut/test-data" ./

echo '[pyflakes]'
pyflakes *.py guiapp/*.py ut/*.py

echo '[desktop-file-validate]'
desktop-file-validate *.desktop
