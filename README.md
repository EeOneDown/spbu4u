[![Build Status](https://travis-ci.org/EeOneDown/spbu4u.svg?branch=master)](https://travis-ci.org/EeOneDown/spbu4u)
[![CodeFactor](https://www.codefactor.io/repository/github/eeonedown/spbu4u/badge)](https://www.codefactor.io/repository/github/eeonedown/spbu4u)
![spbu4u](https://user-images.githubusercontent.com/19958147/45147747-57d8b780-b1ce-11e8-96dd-29549fa29203.png "Spbu4U")

## Spbu4U
Spbu4U is a service for students and teachers of St. Petersburg state University.  Here you can keep track of your schedule, personalize it and always be aware of its changes.  


## Getting started with Telegram
Username: @Spbu4UBot ([link](https://t.me/Spbu4UBot))


## pythonanywhere deploy
* create venv
  * `mkvirtualenv --python=/usr/bin/python3.6 <env-name>`
  * `workon <env-name>`
  * run `pip install -r requirements.txt`
  * fix `pip install pyTelegramBotAPI==3.6.6 spbuTimeTableAPI==1.0.2 six`
* create manual web app
* create db (mysql)
* set ut8 charset
  * `ALTER DATABASE <db-name> CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
* create `.env` file
  * `DATABASE_URL="mysql+pymysql://{user}:{pass}@{host}/{db}"`
* update constants - `app/constants.py`
  * `webhook_host = "<host>"`
* run `flask db upgrade`
* run `python first_deploy.py`
* setup WSGI
  * `from spbu4u_flask.py import app as application`
* go to `<host>/tg/reset_webhook`
* success


## local docker deploy (polling)
* `docker-compose build up -d`
* `docker-compose down`

## local deploy
* mysql
  * if docker:
    * `docker run --name=mysqldb --env="MYSQL_ROOT_PASSWORD=<root_password>" -p 3306:3306 -d mysql:latest`
    * `docker exec -it mysqldb mysql -u root -p <root_password>`
  * `CREATE DATABASE spbu4u;`
  * `ALTER DATABASE spbu4u CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
  * `CREATE USER 'spbu4u'@'%' IDENTIFIED BY '<password>';`
  * `GRANT ALL PRIVILEGES ON spbu4u.* to 'spbu4u'@'%';`
* update `.env`
  * `DATABASE_URL="mysql+pymysql://spbu4u:<password>@localhost:3306/spbu4u"`
* run `flask db upgrade`
* run `python first_deploy.py`
  * troubleshooting `pip install cryptography`
* run `python spbu4u_tg.py`
