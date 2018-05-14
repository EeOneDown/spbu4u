#!/usr/bin/env bash

dir_path=$1

if ! [ -d "$dir_path/logs/" ]; then
    mkdir "$dir_path/logs"
    ls
fi

${dir_path}/venv/bin/python ${dir_path}/schedule_sender.py 1>>${dir_path}/logs/schedule_sender_log.txt 2>>${dir_path}/logs/schedule_sender_err.txt
