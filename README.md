# Twitch Stream Tracker

**Русский** · [English](README.en.md)

Telegram-бот сообщает о начале и завершении эфиров на Twitch. Пользователь добавляет каналы по ссылке, смотрит их статус и может удалить канал из своего списка. Без подписки доступен один канал.

Администраторы могут смотреть статистику, менять цену подписки, выдавать доступ вручную, управлять блокировками и делать рассылки через `/admin`. В боте есть оплата через ЮMoney и отдельная кнопка проверки платежа.

## Запуск

Понадобятся Python 3.10+, бот в Telegram и приложение в Twitch Developer Console. [BotFather](https://t.me/BotFather) · [Регистрация приложения Twitch](https://dev.twitch.tv/docs/authentication/register-app/)

```bash
git clone https://github.com/deco9er/twich-tracker.git
cd twich-tracker
```

**Windows (CMD)**

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install "aiogram>=3.7,<4" "SQLAlchemy[asyncio]>=2,<3" aiosqlite requests
```

**Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install 'aiogram>=3.7,<4' 'SQLAlchemy[asyncio]>=2,<3' aiosqlite requests
```

Заполните существующий `config.py` в своей локальной копии. Перед коммитом проверьте, что рабочие токены и база SQLite остались только у вас.

| Настройка | Что указать |
| --- | --- |
| `BOT_TOKEN` | Токен бота от BotFather. |
| `ADMIN_ID` | Список числовых Telegram ID администраторов, например `[123456789]`. |
| `TWITCH_CLIENT_ID`, `TWITCH_ACCESS_TOKEN` | Client ID приложения и OAuth app access token из client credentials flow. При истечении срока выпустите новый токен и перезапустите бот. |
| `SUPPORT_URL`, `BOT_URL` | Ссылка на поддержку и ссылка на бота для возврата после оплаты. |
| `DB_LITE` | URL SQLite. Можно оставить значение из репозитория. |
| `YOOMONEY_WALLET_ID`, `YOOMONEY_ACCESS_TOKEN` | Кошелёк и токен доступа к истории операций, если нужна оплата подписки. |

[Получение токена Twitch](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#client-credentials-grant-flow)

Запустите бота из папки проекта.

```cmd
.venv\Scripts\python.exe app.py
```

```bash
.venv/bin/python app.py
```

Бот сам создаст таблицы SQLite. Отправьте ему `/start` в личном чате и добавьте ссылку вида `https://www.twitch.tv/username`. Для проверки уведомлений используйте канал, у которого можно начать и завершить эфир.

## Как устроен проект

- `app.py` запускает aiogram, подключает обработчики и запускает фоновый мониторинг.
- `handlers/` обрабатывает команды, подписки и действия администратора.
- `services/` запрашивает Twitch Helix и ЮMoney. Фоновый цикл проверяет каналы из базы, отправляет уведомления при смене статуса и ждёт 10 секунд перед следующим проходом.
- `database/` хранит пользователей, каналы и подписки через SQLAlchemy и SQLite.
