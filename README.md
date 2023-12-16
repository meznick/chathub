# chathub
Chat platform for experiments

# Deploy
### Backend
```shell
cd server
python -m venv venv
pip install -r requirements.txt
python chat_server.py
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
docker run -e POSTGRES_PASSWORD=password -p 5432:5432 chathub-postgres:latest
```
