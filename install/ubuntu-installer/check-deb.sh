#!/usr/bin/env bash

cd deb

echo '[lintian]'
lintian *.changes

echo '[lintian4py]'
lintian4py *.changes

cd ..

