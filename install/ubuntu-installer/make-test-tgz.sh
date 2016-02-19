#!/usr/bin/env bash

SRC_DIR="../../"
PROGRAM_NAME="vizigrep"
VERSION=`cat $SRC_DIR\.version`
PKG_TREE_NAME=$PROGRAM_NAME-$VERSION
GITHUB_TAR_NAME=v"$VERSION".tar.gz

# Remove old package tree
rm -rf /tmp/$PKG_TREE_NAME

# Make & populate folder containing fake release
cp -a $SRC_DIR. /tmp/$PKG_TREE_NAME # Yes, the . is important. It causes hidden files to be copied.

# Tar.gz it!
cd /tmp
tar -zcf $GITHUB_TAR_NAME $PKG_TREE_NAME

# Move tgz to proper location
cd -
mv /tmp/$GITHUB_TAR_NAME ./

# Cleanup
rm -rf /tmp/$PKG_TREE_NAME
