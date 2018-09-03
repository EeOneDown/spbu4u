#!/usr/bin/env bash

cd $1

if [ ! -d logs ]; then
    mkdir logs
    touch schedule_sender_out.log schedule_sender_err.log
fi

venv/bin/python tg_schedule_sender.py 1>>logs/schedule_sender_out.log 2>>logs/schedule_sender_err.log
