#!/usr/bin/env bash

SRC_DIR="../../"
TGZ_DIR="../"
PROGRAM_NAME="vizigrep"
VERSION=`cat $SRC_DIR\.version`
PKG_TREE_NAME=$PROGRAM_NAME-$VERSION

# Remove old package tree & DEB files
rm -rf $PKG_TREE_NAME
rm -rf ./deb

#Construct '.orig' original source package to satisfy debian convention
cd $TGZ_DIR
./make-generic-release.sh
cd -
cp $TGZ_DIR/$PROGRAM_NAME'_'$VERSION.tar.gz ./$PROGRAM_NAME'_'$VERSION.orig.tar.gz
pwd
ls
tar -zxf $PROGRAM_NAME'_'$VERSION.orig.tar.gz

# Inject debian build specific files
cp -a debian $PKG_TREE_NAME/

# Inject debian compatable changelog
cp -a $SRC_DIR/changelog $PKG_TREE_NAME/debian/

# Build!
cd $PKG_TREE_NAME/
debuild
cd ..

# Cleanup
mkdir -p  deb
mv *.deb *.tar.gz *.dsc *.build *.changes  deb/
rm -rf $PKG_TREE_NAME

