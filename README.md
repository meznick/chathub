# chathub
Chat platform for experiments

# Develop
Backend:
```shell
cd server
python -m venv venv
# first build chathub packages (below) or install them as editable with pip (pip install -e)
pip install -r requirements.txt  # base requirements
cd api
pip install -r requirements.txt  # FastAPI requirements
# websocket
python sever.py
# fastapi
uvicorn api:app --reload
```

Frontend:
```shell
# надо повспоминать как ставить окружение
npm run dev
```

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
