#!/bin/bash

set -e

ASSERT_BIN=$1

fail() {
    echo "TEST FAILED: $1" >&2
    exit 1
}

assertExists(){
    P=$1

    if [ ! -e "$P" ]
    then
        fail "Expected path to exist: $P"
    fi
}

assertLink(){
    P=$1

    assertExists "$P"

    if [ ! -L "$P" ]
    then
	fail "Expected path to be link: $P"
    fi
}

assertDir(){
    P=$1

    assertExists "$P"

    if [ ! -d "$P" ]
    then
        fail "Expected path to be a directory: $P"
    fi
}

assertEqualContent(){
    cmp "$1" "$2" > /dev/null || fail "File content is not equal: $1 and $2 ($DIFF)"
}

cd `dirname "$ASSERT_BIN"`
. $ASSERT_BIN > "$ASSERT_BIN.log"
