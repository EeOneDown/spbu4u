[![Build Status](https://travis-ci.org/EeOneDown/spbu4u.svg?branch=master)](https://travis-ci.org/EeOneDown/spbu4u)
[![CodeFactor](https://www.codefactor.io/repository/github/eeonedown/spbu4u/badge)](https://www.codefactor.io/repository/github/eeonedown/spbu4u)
![spbu4u](https://user-images.githubusercontent.com/19958147/45147747-57d8b780-b1ce-11e8-96dd-29549fa29203.png "Spbu4U")

## Spbu4U
Spbu4U is a service for students and teachers of St. Petersburg state University.  Here you can keep track of your schedule, personalize it and always be aware of its changes.  


## Getting started with Telegram
Username: @Spbu4UBot ([link](https://t.me/Spbu4UBot))


## pythonanywhere deploy
* create venv
  ```bash
  mkvirtualenv --python=/usr/bin/python3.6 <env-name>
  workon <env-name>
  pip install -r requirements.txt
  ```
* create manual web app
* create db (mysql)
* set ut8 charset
  ```SQL
  ALTER DATABASE <db-name> CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```
* create `.env` file from `.env_example`
* run migrations
  ```bash
  workon <env-name>
  flask db upgrade
  python first_deploy.py
  ```
* fix DB
  ```SQL
  ALTER TABLE users MODIFY tg_id BIGINT NOT NULL;
  ```
* setup WSGI
  ```Python
  from spbu4u_flask.py import app as application
  ```
* navigate to `<host>/tg/reset_webhook`
* success


## local docker deploy (polling)
* install docker
* create `.env` file from `.env_example`
* to build and run
  ```bash
  docker-compose up --build -d
  ```
* to stop  
  ```bash
  docker-compose down
  ```

## local deploy
* mysql
  * if docker:
    ```bash
    # init mysql
    docker run --name=mysqldb --env="MYSQL_ROOT_PASSWORD=<root_password>" -p 3306:3306 -d mysql:latest
    # connect as root
    docker exec -it mysqldb mysql -u root -p <root_password>
    ```
  * Setup DB
  ```SQL
  CREATE DATABASE spbu4u;
  ALTER DATABASE spbu4u CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  CREATE USER 'spbu4u'@'%' IDENTIFIED BY '<password>';
  GRANT ALL PRIVILEGES ON spbu4u.* to 'spbu4u'@'%';
  ```
* create `.env` file from `.env_example`
* create and activate virtualenv for Python 3.6
* run migrations
  ```bash
  flask db upgrade
  python first_deploy.py
  ```
* start bot polling
  ```bash
  python spbu4u_tg.py
  ```
