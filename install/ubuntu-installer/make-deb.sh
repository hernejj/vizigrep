#!/usr/bin/env bash

SRC_DIR="../../"
TGZ_DIR="../"
PROGRAM_NAME="vizigrep"
VERSION=`cat $SRC_DIR\.version`
PKG_TREE_NAME=$PROGRAM_NAME-$VERSION

# Remove old package tree & DEB files
rm -rf $PKG_TREE_NAME
rm -rf ./deb

# Generate and Unpack source
cd $TGZ_DIR
./make-generic-release.sh
cd -
tar -zxf $TGZ_DIR/$PROGRAM_NAME-$VERSION.tgz

# Inject debian build specific files
cp Makefile $PKG_TREE_NAME/
cp vizigrep.sh $PKG_TREE_NAME/
cp -a debian $PKG_TREE_NAME/

# Build!
cd $PKG_TREE_NAME/
debuild
cd ..

# Cleanup
mkdir -p  deb
mv *.deb *.tar.gz *.dsc *.build *.changes deb/
#rm -rf $PKG_TREE_NAME
