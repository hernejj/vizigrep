#!/usr/bin/env bash

PKG_TREE_NAME="vizigrep"
SRC_DIR="../../"

# Remove old package tree & DEB file, and create new package tree
rm -rf $PKG_TREE_NAME
rm -f ./*.deb
mkdir $PKG_TREE_NAME

# Copy source
cp $SRC_DIR/* $PKG_TREE_NAME/

# Copy build related files
cp Makefile $PKG_TREE_NAME/
cp vizigrep.sh $PKG_TREE_NAME/
cp -a debian $PKG_TREE_NAME/
cp vizigrep.man $PKG_TREE_NAME/

# Build!
cd $PKG_TREE_NAME/
debuild && cd .. && rm -rf ./$PKG_TREE_NAME

