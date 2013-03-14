#!/usr/bin/env bash

PKG_TREE_NAME="vizigrep"
SRC_DIR="../"
VERSION=`cat $SRC_DIR\.version`

# Remove old package tree & tgz file, and create new package tree
rm -rf $PKG_TREE_NAME
rm -f ./*.tgz
mkdir $PKG_TREE_NAME

# Copy source
cp $SRC_DIR/*.py $PKG_TREE_NAME/
cp $SRC_DIR/*.glade $PKG_TREE_NAME/
cp $SRC_DIR/README $PKG_TREE_NAME/
cp $SRC_DIR/vizigrep.svg $PKG_TREE_NAME/

# Copy manpage & update version number
cat $SRC_DIR/vizigrep.man | sed s/vizigrep-[0-9]*[.][0-9]*/vizigrep-$VERSION/ > $PKG_TREE_NAME/vizigrep.man

# Create tgz package
tar -zcf $PKG_TREE_NAME-$VERSION.tgz $PKG_TREE_NAME/
