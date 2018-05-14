#!/usr/bin/env bash

if ! [ -d $HOME/spbu4u/logs/ ]; then
    mkdir '$HOME/spbu4u/logs'
    ls
fi

$HOME/spbu4u/venv/bin/python $HOME/spbu4u/schedule_sender.py 1>>$HOME/spbu4u/logs/schedule_sender_log.txt 2>>$HOME/spbu4u/logs/schedule_sender_err.txt
