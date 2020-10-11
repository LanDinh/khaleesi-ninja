# khaleesi-ninja

![licence](https://img.shields.io/badge/license-MIT-informational)
[![Build Status](https://travis-ci.com/LanDinh/khaleesi-ninja.svg?branch=master)](https://travis-ci.com/LanDinh/khaleesi-ninja)
[![Code Coverage Status](https://codecov.io/gh/LanDinh/khaleesi-ninja/branch/master/graph/badge.svg)](https://codecov.io/gh/LanDinh/khaleesi-ninja)

## Backend

![postgres version](https://img.shields.io/badge/PostgreSQL-v12-informational)
![python version](https://img.shields.io/badge/Python-v3.8-informational)
![django version](https://img.shields.io/badge/Django-v3.1-informational)

### Setup

You can take a look at `scripts/backend_install.sh` for an example.

1. Setup the code part.
    1. Install `python`. I'm using 3.8, but any 3+ should be fine.
    1. Setup your favorite `python` virtual environment and activate it.
       I'm using the standard library `venv`.
    1. Install the dependencies using `pip install -r backend/requirements.txt`.
1. Setup the common.configuration.
    1. Install `PostgreSQL`. I'm using 12.
    1. Start the database.
    1. Install citext on `template1`, otherwise the tests will fail.
    1. Create a database user with permissions to create databases.
    1. Create the database.
    1. Provide the database and user information in `backend/common/configuration/settings.py`
1. Populate the database.
    1. `backend/common/manage.py migrate`

### Testing & Co

For the following commands, `<project>` specifies which microservice you want to start.
You can find and example at `scripts/backend_run.sh`.

* Tests: `backend/<project>/manage.py test`. You can specify the tags `unit` and `integration`.
* Linter: `pylint backend/<project>/`
* Static Type Checker: `mypy --strict <project>/`.
  Remember to add the backend package to your `PYTHONPATH`.
    * This needs to run from within `backend`.

## Frontend

![typescript version](https://img.shields.io/badge/Typescript-v3.7-informational)
![reactjs version](https://img.shields.io/badge/ReactJS-v16.13-informational)

### Setup

1. Setup the code part.
  * Install `node`. I'm using 12.16, but any somewhat recent version should be fine.
  * Install the dependencies using `npm install`.

### Testing & Co

* Tests: `npm --prefix frontend test`
* Linter: `npm --prefix frontend run lint`

### Running the development server

1. Make sure the backend is running.
1. `npm start`
