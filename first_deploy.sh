#!/usr/bin/env bash

export FLASK_APP=spbu4u_flask.py
flask db upgrade

python first_deploy.py
