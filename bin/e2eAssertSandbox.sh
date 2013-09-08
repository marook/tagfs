#!/bin/bash

set -e

ASSERT_BIN=$1

fail() {
    echo "TEST FAILED: $1" >&2
    exit 1
}

assertExists(){
    local path="$1"

    if [ ! -e "${path}" ]
    then
        fail "Expected path to exist: ${path}"
    fi
}

assertNotExists(){
    local path="$1"

    if [ -e "${path}" ]
    then
        fail "Expected path to not exist: ${path}"
    fi
}

assertLink(){
    local path="$1"

    assertExists "${path}"

    if [ ! -L "${path}" ]
    then
	fail "Expected path to be link: ${path}"
    fi
}

assertDir(){
    local path="$1"

    assertExists "${path}"

    if [ ! -d "${path}" ]
    then
        fail "Expected path to be a directory: ${path}"
    fi
}

assertEqualContent(){
    cmp "$1" "$2" > /dev/null || fail "File content is not equal: $1 and $2 ($DIFF)"
}

cd `dirname "$ASSERT_BIN"`
. $ASSERT_BIN > "$ASSERT_BIN.log"
