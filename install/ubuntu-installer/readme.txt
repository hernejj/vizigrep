make-deb.sh
--------------
This script is used to create an installable deb and associated files that are
required for uploading the package to a Debian repository. The output files are
put into ./deb.

make-deb.sh has a few dependencies. Make sure to install them:
    devscripts python-all-dev debhelper dh-python

This script downloads a source package from the project's Github page. By default
it will use the package obtained by downloading the tag v$VERSION where $VERSION
is the contents of the file vizigrep/.version. This source package is then used
to generate the deb.

make-test-tgz.sh
-------------------
This script is used to generate a source package using the local copy of the
code. It is useful for installing and testing the code before you commit it to
Git and/or before you set a release tag on Github. Just run make-test-tgz.sh
followed by make-deb.sh.

