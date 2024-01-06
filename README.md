# chathub
Chat platform for experiments

# Deploy
### Backend
```shell
cd server
python -m venv venv
pip install -r requirements.txt
# websocket
python sever.py
# fastapi
uvicorn api:app --reload
```

### Frontend
dev
```shell
# надо повспоминать как ставить окружение
npm run dev
```

prod
```shell
# пока хз)
```

### DB
```shell
# setup
cd deploy/db
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

### MQ
```shell
cd deploy/mq
docker build -t chathub-rmq:latest -f Dockerfile .
docker run -d --hostname chathub-rmq --name chathub-rmq \
-p 8081:15672 \
chathub-rmq:latest
```

### Redis
```shell
cd deploy/redis
docker build -t chathub-redis:latest -f Dockerfile .
docker run -d --hostname chathub-redis --name chathub-redis -p 6379:6379 chathub-redis:latest
```


## Run tests
```shell
# chathub_utils: from /utils dir:
python -m unittest tests/test_auth.py -v
```
