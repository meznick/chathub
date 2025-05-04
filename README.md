# chathub
A chat platform for experimentation.

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

# Run tests
```shell
# chathub_utils: from /utils dir:
python -m unittest tests/test_auth.py -v
```

# Deploy
Backend
```shell
docker build -t chathub-api:latest .
docker run --rm --hostname chathub-api --name chathub-api \
-p 8888:8888 -d chathub-api:latest
```

Frontend
```shell
# пока хз)
```

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
