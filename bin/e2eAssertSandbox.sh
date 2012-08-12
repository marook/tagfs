#!/bin/bash

ASSERT_BIN=$1

fail() {
    echo "$1" >&2
    exit 1
}

assertLink(){
    PATH=$1

    if [ ! -L "$PATH" ]
    then
	fail "Expected path to be link: $PATH"
    fi
}

. $ASSERT_BIN
