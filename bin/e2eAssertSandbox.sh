#!/bin/bash

set -e

ASSERT_BIN=$1

fail() {
    echo "TEST FAILED: $1" >&2
    exit 1
}

assertLink(){
    PATH=$1

    if [ ! -L "$PATH" ]
    then
	fail "Expected path to be link: $PATH"
    fi
}

assertDir(){
    PATH=$1

    if [ ! -d "$PATH" ]
    then
        fail "Expected path to be a directory: $PATH"
    fi
}

assertEqualContent(){
    cmp "$1" "$2" > /dev/null || fail "File content is not equal: $1 and $2 ($DIFF)"
}

cd `dirname "$ASSERT_BIN"`
. $ASSERT_BIN > "$ASSERT_BIN.log"
