#!/usr/bin/env bash

if ! [ -d $HOME/spbu4u/logs/ ]; then
    mkdir '$HOME/spbu4u/logs'
    ls
fi

python schedule_sender.py 1>>logs/schedule_sender_log.txt 2>>logs/schedule_sender_err.txt
