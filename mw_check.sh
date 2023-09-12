#!/usr/bin/env bash

check_cards(){
    # Check cards
    CARDS=$(sudo -u root mwcap-info -l | grep video -c)
    if (($CARDS>=1)); then
        echo "OK - ${CARDS} video inputs."
        exit 0
    elif (($CARDS>=81)); then
        echo "WARNING - ${CARDS} video inputs."
        exit 1
    elif (($CARDS==0)); then
        echo "CRITICAL - ${CARDS} of video inputs."
        exit 2
    else
        echo "UNKNOWN - ${CARDS} of video inputs."
        exit 3
    fi
}


check_cards
