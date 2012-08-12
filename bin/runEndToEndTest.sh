#!/bin/bash

set -e

TEST_DIR=$1

fail() {
    echo "$1" >&2
    exit 1
}

cleanupTagFS(){
    fusermount -u $TEST_MOUNT_DIR
    rmdir $TEST_MOUNT_DIR
}

if [ ! -d "$TEST_DIR" ]
then
    fail "TEST_DIR is not a directory: $TEST_DIR"
fi

TEST_NAME=`basename $TEST_DIR`

echo ''
echo '======================================================'
echo "  Executing end-to-end test $TEST_NAME"

PYTHON=python

BIN_DIR=`dirname "$0"`
PROJECT_DIR=$BIN_DIR/..
PYMODDIR=$PROJECT_DIR/src/modules
export PYTHONPATH=$PYMODDIR:$PYTHONPATH

export TEST_MOUNT_DIR=`mktemp -d --tmpdir tagfs_e2e.$TEST_NAME.XXXXXXXXXX`

echo "Using mount $TEST_MOUNT_DIR"

$PYTHON $PROJECT_DIR/src/bin/tagfs -i $TEST_DIR/items $TEST_MOUNT_DIR

trap cleanupTagFS EXIT

echo 'Asserting mount'

$BIN_DIR/e2eAssertSandbox.sh $TEST_DIR/assert

echo "Success"
