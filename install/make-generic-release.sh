#!/usr/bin/env bash

SRC_DIR="../"
PROGRAM_NAME="vizigrep"
VERSION=`cat $SRC_DIR\.version`
PKG_TREE_NAME=$PROGRAM_NAME-$VERSION

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
tar -zcf $PROGRAM_NAME-$VERSION.tgz $PKG_TREE_NAME/

# Remove temp junk
rm -rf $PKG_TREE_NAME
