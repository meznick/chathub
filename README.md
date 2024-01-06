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
cd deploy/db
docker build -t chathub-postgres:latest -f pg-Dockerfile .
docker run -e POSTGRES_PASSWORD=password \
-v $HOME/Documents/pg-data:/var/lib/postgresql/data \
--hostname chathub-pg --name chathub-pg \
-p 5432:5432 -d chathub-postgres:latest
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
