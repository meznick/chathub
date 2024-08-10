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