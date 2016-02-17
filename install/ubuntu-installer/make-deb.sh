#!/usr/bin/env bash

SRC_DIR="../../"
PROGRAM_NAME="vizigrep"
VERSION=`cat $SRC_DIR\.version`
PKG_TREE_NAME=$PROGRAM_NAME-$VERSION
GITHUB_TAR_NAME=v"$VERSION".tar.gz
ORIG_TAR_NAME=$PROGRAM_NAME'_'$VERSION.orig.tar.gz

# Remove old package tree & DEB files
rm -rf $PKG_TREE_NAME
rm -rf ./deb

#Fetch '.orig' original source package if we don't already have it
if [ ! -f $GITHUB_TAR_NAME ]; then
    wget https://github.com/hernejj/vizigrep/archive/$GITHUB_TAR_NAME    
fi
 
if [ ! -f $GITHUB_TAR_NAME ]; then
    echo "Could not download $GITHUB_TAR_NAME from Github"
    exit $?
fi

# Deb build process expects to find an original .tar.gz with a very specific name
cp -a $GITHUB_TAR_NAME $ORIG_TAR_NAME

# Unpack orig source package - this creates a folder named $PKG_TREE_NAME
tar -zxf $GITHUB_TAR_NAME

# Copy debian build specific files to expected location
cp -a $PKG_TREE_NAME/install/ubuntu-installer/debian $PKG_TREE_NAME/

# Build!
cd $PKG_TREE_NAME/
pwd
debuild
cd ..

# Place all files neeed for a debian release into ./deb
mkdir -p  deb
mv *.deb *.dsc *.build *.changes  deb/
mv  $ORIG_TAR_NAME deb/
mv $PROGRAM_NAME'_'$VERSION'-1.debian.tar.gz' deb/

# Cleanup
rm -rf $PKG_TREE_NAME
