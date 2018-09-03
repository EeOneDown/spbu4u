#!/usr/bin/env bash

dir_path=$1

if ! [ -d "$dir_path/logs/" ]; then
    mkdir "$dir_path/logs"
fi

${dir_path}/venv/bin/python ${dir_path}/tg_schedule_sender.py 1>>${dir_path}/logs/schedule_sender_out.log 2>>${dir_path}/logs/schedule_sender_err.log
