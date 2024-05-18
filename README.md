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
---
Все что ниже -- нужно вынести в отдельную от проекта репу для переиспользования
в других.

Postgres
```shell
# setup
cd deploy/pg
docker build -t chathub-postgres:latest -f pg-Dockerfile .
docker run -e POSTGRES_PASSWORD=password \
-v $HOME/Documents/pg-data:/var/lib/postgresql/data \
--hostname chathub-pg --name chathub-pg \
-p 5432:5432 -d chathub-postgres:latest
# terraform initiation
terraform plan
terraform apply # set variables when deploying to prod!
# migrations
sudo pacman -S dbmate
export DATABASE_URL=postgres://dev_developer:devpassword@localhost:5432/chathub_dev?sslmode=disable
# new migration
dbmate new "migration_name" # do not forget grants!
# use sqlfluff on created migration before making commit!
sqlfluff lint filename.sql --dialect postgres
sqlfluff fix filename.sql --dialect postgres
dbmate up # perform migrations
dbmate rollback # revert last batch of migrations
```

RabbitMQ
```shell
cd deploy/mq
docker build -t chathub-rmq:latest -f Dockerfile .
docker run -d --hostname chathub-rmq --name chathub-rmq \
-p 15672:15672 \
-p 5672:5672 \
chathub-rmq:latest
```

Redis
```python
# generating password hash for ACL
import hashlib
hashlib.sha256(''.encode()).hexdigest()
```
```shell
cd deploy/redis
docker build -t chathub-redis:latest -f Dockerfile .
docker run -d --hostname chathub-redis --name chathub-redis -p 6379:6379 chathub-redis:latest
```

Package registry (pypiserver)
```shell
# later create systemd daemon
pip install pypiserver
mkdir ~/pypi_packages
# listening only inside VPN
pypi-server run -p 8228 -i 10.132.179.1 -a . -P . /home/meznick/pypi_packages --verbos

# pushing packages: on dev machine
pip install twine build
cd connectors
python -m build
# signing is optional
twine upload --repository-url http://10.132.179.1:8228 dist/* --verbose
```
