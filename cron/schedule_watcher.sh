#!/usr/bin/env bash

cd $1

if [ ! -d logs ]; then
    mkdir logs
    touch logs/schedule_watcher_out.log logs/schedule_watcher_err.log
fi

venv/bin/python schedule_watcher.py 1>>logs/schedule_watcher_out.log 2>>logs/schedule_watcher_err.log