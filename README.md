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
-v $HOME/Documents/Projects/chathub/deploy/db/pg-data:/var/lib/postgresql/data \
-p 5432:5432 -d chathub-postgres:latest
```
