# chathub
A chat platform for experimentation. This is file with installation and some
technical instructions.
For business logic descriptions look other md files in modules.

# Modules
Description for every module look inside module's directory.
API: No readme yet.
Bot: [readme.md](chathub_bot/readme.md)
Client: [README.md](client/README.md)
Connectors: [readme.md](connectors/readme.md)
Datemaker: [readme.md](datemaker/readme.md)
Matchmaker: No readme yet.
WebSocket: No readme yet.

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
# Env files
All env variables are written in different files to restrict different services.
Files are located in `/home/infra/.env_files`.

To get working env configuration you need to concatenate multiple files into one
according to list of env params in readme files for each service.

```shell
cd ~/.env_files
# tg bot
cat prod aws pg rabbitmq tg_bot > tg_bot_prod
cat dev aws pg rabbitmq tg_bot > tg_bot_dev
# datemaker
cat prod aws pg rabbitmq datemaker > datemaker_prod
cat dev aws pg rabbitmq datemaker > datemaker_dev
# params for infra deployment
cat aws pg rabbitmq admin > deploy
# migrations
cat pg dev migrations > migrations_dev
cat pg prod migrations > migrations_prod
```
