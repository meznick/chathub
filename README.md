# chathub
A chat platform for experimentation. This is file with installation and some
technical instructions.
For business logic descriptions look other md files in modules.

# Modules
Here's a description and installation instructions of each included module.
## API
Fastapi based async API endpoints for later use in web app.
```shell
# create python venv any way you prefer
python -m venv venv
source venv/bin/activate
cd api
# installing requirements for this module
pip install -r requirements.txt
# running API server
uvicorn api:app --reload
```
Utils is cross-module code that potentially can be used. This module can 
easily be installed as connectors modules. But not now, now it's abandoned
until working on API.

## WebSocket
Module for handling websocket connections.
```shell
# installation goes same way as in API section
# running server is done like this
python sever.py
```

## Client
This is a VueJS based web app that can use API and websocket.
```shell
# to be written later
npm run dev
```

## Connectors
Module includes connectors for AWS, PG, RabbitMQ, Redis.

Build module in activated venv:
```shell
make build
```

Install module in editable mode for development in activated venv:
```shell
pip install -e .
```

Upload to repository:
```shell
make upload  # update repository url in makefile
```

Install from repository:
```shell
pip install --index-url http://007pi.loc:8228 chathub_connectors
```

# Run tests
Update this section in PR for adding tests.

# Deploy
If you want to see the deploy instructions, look in the infra repo.

# PG migrations
```shell
sudo pacman -S dbmate
source ~/.env
# new migration
dbmate new "migration_name" # do not forget grants!
# use sqlfluff on created migration before making commit!
sqlfluff lint filename.sql --dialect postgres
sqlfluff fix filename.sql --dialect postgres
dbmate up # perform migrations
dbmate rollback # revert last batch of migrations
```
