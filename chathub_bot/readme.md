# tg bot
Функционал:
- юзер может зарегистрироваться, указать: город, пол, дата рождения, фотки
- юзер может редактировать профиль: менять все указанное выше
- юзер может подать заявку на событие
- юзеру перед событием отправляется подтверждение, он должен подтвердить\отменить
- непосредственно функционал спиддейтинга

## Клиент
### Регистрация
Первым действием в боте всегда является отправка человеком команды `/start`.
По этой команде нужно отправить какое-то приветствие и предоставить интерфейс для
заполнения личных данных. Тут нужно подумать как это сделать -- 
[в чате](https://core.telegram.org/bots/features)
или открывать [мини апп](https://core.telegram.org/bots/webapps).

## DB
Нужно подумать что хранить о юзерах чтобы:
- оценивать социальный рейтинг (не отпускаю эту идею, но опционально)
- реагировать на репорты, выявлять пакостников и банить
- анализировать поведение юзеров для улучшения UX

## Бекенд
Обработка взаимодействия с юзером по его действиям в окне чата 
(в т.ч. ответы на подтверждение). Это через [фреймворк](docs.aiogram.dev) бота.

Обработка запросов от мини-аппки. Это через API.

Генерация "событий", отправка подтверждений юзерам. Это отдельные сервисы.

Разные части между собой общаются по брокеру сообщений.

## Формат сообщений в RabbitMQ 
Смотри раздел с таким названием в readme для date maker.

## Разработка
### Работа с локализацией
Пример работы со строкой, которая будет отображаться у юзеров по-разному
в зависимости от настроек языка:
```python
from aiogram.utils.i18n import gettext as _

@on.message()
async def on_enter(self, message, state):
    await message.answer(
        _("Hello, {name}!").format(name=message.from_user.full_name)
    )
```

При этом в файле `.pot` должна быть строчка: `msgid "Hello, {name}!"`, а в
файлах `.po` будут строки:
```
msgid "Hello, {name}!"
msgstr "Привет, {name}!"
```

Если в ходе доработок добавилось новая строка, требующая локализации,
например сообщение, которое нужно отправить юзеру, то необходимо обновить
файлы локалей:
```shell
cd chathub_bot
pip install -r requirements.txt
make update_templates
```

После добавления переводов, необходимо выполнять `make compile` для того чтобы
получить файлы `.mo` которые используются при исполнении кода.

Эта команда обновит файлы в `bot/locales`: создаст заготовки, в которые нужно
будет вписать переводы для каждого из языков.

В коммит включаем только файлы `.po`, `.pot`.

## Deploy
```shell
pip install -r requirements.txt
make compile
source ~/.env
python -m bot --debug --long-polling
```

## Environment Variables
The following environment variables are required for running the bot module:

### General Configuration
- `BOT_VARIABLES_LOADED` - Controls whether to load variables from the .env file. Always set to true
- `DEBUG` - Controls logging level and routing key
- `TG_BOT_TOKEN` - Telegram bot token

### RabbitMQ Configuration
- `RABBITMQ_HOST` - RabbitMQ host
- `RABBITMQ_PORT` - RabbitMQ port
- `RABBITMQ_VIRTUAL_HOST` - RabbitMQ virtual host
- `TG_BOT_RABBITMQ_EXCHANGE` - RabbitMQ exchange to read from for the bot
- `TG_BOT_RABBITMQ_QUEUE` - RabbitMQ queue to read from for the bot
- `TG_BOT_RABBITMQ_USERNAME` - RabbitMQ username for the bot
- `TG_BOT_RABBITMQ_PASSWORD` - RabbitMQ password for the bot

### PostgreSQL Configuration
- `POSTGRES_HOST` - PostgreSQL host
- `POSTGRES_PORT` - PostgreSQL port
- `POSTGRES_DB` - PostgreSQL database name
- `TG_BOT_POSTGRES_USER` - PostgreSQL username for the bot
- `TG_BOT_POSTGRES_PASSWORD` - PostgreSQL password for the bot

### AWS Configuration
- `AWS_ACCESS_KEY_ID` - AWS access key ID
- `AWS_SECRET_ACCESS_KEY` - AWS secret access key
- `AWS_BUCKET` - AWS S3 bucket name

These environment variables should be set in the `.env` file that is sourced 
before running the bot.
