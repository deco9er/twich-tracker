# Twitch Stream Monitor Bot

Telegram бот для отслеживания статуса стримов на Twitch. Позволяет пользователям добавлять Twitch каналы в список отслеживания и получать уведомления о начале и завершении стримов.

## 🚀 Функционал

### Для пользователей:
- **👤 Профиль** - просмотр информации о пользователе, количестве отслеживаемых каналов и статусе подписки
- **➕ Добавление каналов** - добавление Twitch каналов для отслеживания по ссылке
- **📋 Список каналов** - просмотр всех добавленных каналов с их текущим статусом (online/offline)
- **💎 Подписка** - платная подписка для снятия ограничений
- **🛠 Техподдержка** - прямая ссылка на поддержку

### Для администраторов:
- **📊 Статистика** - общая статистика по пользователям, подпискам и каналам
- **💰 Управление ценой** - изменение стоимости подписки
- **👥 Управление пользователями** - бан/разбан пользователей
- **💎 Выдача подписки** - ручная выдача подписки пользователям
- **📢 Рассылка** - массовая рассылка сообщений всем пользователям

## 🛠 Технический стек

- **Python 3.10+**
- **Aiogram 3.x** - асинхронный фреймворк для Telegram Bot API
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **SQLite + aiosqlite** - база данных
- **Twitch API** - проверка статуса стримов
- **ЮMoney API** - интеграция с платежной системой

## 📁 Структура проекта

```
├── app.py                 # Главный файл запуска бота
├── config.py              # Конфигурация и токены
├── database/
│   ├── engine.py          # Настройка подключения к БД
│   ├── models.py          # Модели SQLAlchemy
│   └── orm_query.py       # ORM запросы
├── filters/
│   └── chat_types.py      # Фильтры для админов
├── handlers/
│   ├── admin_private.py   # Админские команды
│   ├── states.py          # Состояния FSM
│   └── user_private.py    # Пользовательские команды
├── kbrds/
│   ├── inline.py          # Inline клавиатуры
│   └── reply.py           # Reply клавиатуры
├── middlewares/
│   └── db.py              # Middleware для сессий БД
└── services/
    ├── datetime_service.py   # Работа с датами
    ├── payment_service.py    # Интеграция с ЮMoney
    ├── stream_monitor.py     # Мониторинг стримов
    └── twitch_checker.py     # Проверка Twitch API
```

## 📊 Модели данных

### User
- `id` - внутренний идентификатор
- `user_id` - Telegram ID пользователя
- `reg_date` - дата регистрации
- `is_banned` - статус бана
- `channels` - связь с отслеживаемыми каналами
- `subscription` - связь с подпиской

### TwitchChannel
- `id` - идентификатор канала
- `channel_url` - URL Twitch канала
- `channel_name` - имя канала
- `is_live` - текущий статус стрима
- `last_checked` - время последней проверки
- `users` - пользователи, отслеживающие канал

### Subscription
- `id` - идентификатор подписки
- `user_id` - связь с пользователем
- `is_active` - активна ли подписка
- `start_date` - дата начала
- `end_date` - дата окончания
- `payment_id` - ID платежа в ЮMoney

### SubscriptionSettings
- `id` - идентификатор настроек
- `price` - стоимость подписки
- `updated_at` - время последнего обновления

## 🔄 Процесс работы

1. **Мониторинг стримов** - каждые 10 секунд проверяются все каналы в БД
2. **Проверка статуса** - используется Twitch API для определения онлайн/оффлайн статуса
3. **Уведомления** - при изменении статуса, уведомления отправляются всем подписчикам канала
4. **Платежи** - интеграция с ЮMoney для приема платежей и автоматической активации подписок

## ⚙️ Установка и запуск

1. **Клонирование репозитория**
```bash
git clone https://github.com/yourusername/twitch-monitor-bot.git
cd twitch-monitor-bot
```

2. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

3. **Настройка конфигурации**
Создайте файл `config.py`:
```python
BOT_TOKEN = 'ваш_токен_бота'
ADMIN_ID = [ваш_telegram_id]

DB_LITE = "sqlite+aiosqlite:///./database.db"

SUPPORT_URL = "ссылка_на_поддержку"

TWITCH_CLIENT_ID = "twitch_client_id"
TWITCH_ACCESS_TOKEN = "twitch_access_token"

YOOMONEY_WALLET_ID = "номер_кошелька"
YOOMONEY_ACCESS_TOKEN = "токен_юmoney"
YOOMONEY_NOTIFICATION_SECRET = "секрет_уведомлений"
```

4. **Запуск бота**
```bash
python app.py
```

## 🔐 Безопасность

- Все токены и ключи хранятся в отдельном конфигурационном файле
- Проверка прав доступа для админ-команд
- Middleware для управления сессиями БД
- Защита от SQL-инъекций через ORM

## 📝 Лицензия

MIT License

## 👨‍💻 Разработка

### Требования для разработки
- Python 3.10+
- Понимание asyncio
- Знание aiogram 3.x
- Опыт работы с SQLAlchemy
- 

EN
# Twitch Stream Monitor Bot

Telegram bot for tracking Twitch stream status. Allows users to add Twitch channels to their watchlist and receive notifications when streams go live or end.

## 🚀 Features

### For Users:
- **👤 Profile** - View user information, number of tracked channels, and subscription status
- **➕ Add Channels** - Add Twitch channels for tracking via link
- **📋 Channel List** - View all added channels with their current status (online/offline)
- **💎 Subscription** - Paid subscription to remove limitations
- **🛠 Support** - Direct link to customer support

### For Administrators:
- **📊 Statistics** - General statistics on users, subscriptions, and channels
- **💰 Price Management** - Change subscription price
- **👥 User Management** - Ban/unban users
- **💎 Grant Subscription** - Manually grant subscriptions to users
- **📢 Broadcast** - Mass messaging to all users

## 🛠 Tech Stack

- **Python 3.10+**
- **Aiogram 3.x** - Asynchronous framework for Telegram Bot API
- **SQLAlchemy 2.0** - ORM for database operations
- **SQLite + aiosqlite** - Database
- **Twitch API** - Stream status verification
- **YooMoney API** - Payment system integration

## 📁 Project Structure

```
├── app.py                 # Main bot launch file
├── config.py              # Configuration and tokens
├── database/
│   ├── engine.py          # Database connection setup
│   ├── models.py          # SQLAlchemy models
│   └── orm_query.py       # ORM queries
├── filters/
│   └── chat_types.py      # Filters for admin access
├── handlers/
│   ├── admin_private.py   # Admin commands
│   ├── states.py          # FSM states
│   └── user_private.py    # User commands
├── kbrds/
│   ├── inline.py          # Inline keyboards
│   └── reply.py           # Reply keyboards
├── middlewares/
│   └── db.py              # Middleware for DB sessions
└── services/
    ├── datetime_service.py   # Date/time operations
    ├── payment_service.py    # YooMoney integration
    ├── stream_monitor.py     # Stream monitoring
    └── twitch_checker.py     # Twitch API checker
```

## 📊 Data Models

### User
- `id` - Internal identifier
- `user_id` - Telegram user ID
- `reg_date` - Registration date
- `is_banned` - Ban status
- `channels` - Relationship with tracked channels
- `subscription` - Relationship with subscription

### TwitchChannel
- `id` - Channel identifier
- `channel_url` - Twitch channel URL
- `channel_name` - Channel name
- `is_live` - Current stream status
- `last_checked` - Last check timestamp
- `users` - Users tracking this channel

### Subscription
- `id` - Subscription identifier
- `user_id` - Relationship with user
- `is_active` - Whether subscription is active
- `start_date` - Start date
- `end_date` - End date
- `payment_id` - YooMoney payment ID

### SubscriptionSettings
- `id` - Settings identifier
- `price` - Subscription price
- `updated_at` - Last update timestamp

## 🔄 Workflow

1. **Stream Monitoring** - All channels in the database are checked every 10 seconds
2. **Status Verification** - Twitch API is used to determine online/offline status
3. **Notifications** - When status changes, notifications are sent to all channel subscribers
4. **Payments** - YooMoney integration for processing payments and automatic subscription activation

## ⚙️ Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/twitch-monitor-bot.git  
cd twitch-monitor-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure settings**
Create a `config.py` file:
```python
BOT_TOKEN = 'your_bot_token'
ADMIN_ID = [your_telegram_id]

DB_LITE = "sqlite+aiosqlite:///./database.db"

SUPPORT_URL = "support_link"

TWITCH_CLIENT_ID = "twitch_client_id"
TWITCH_ACCESS_TOKEN = "twitch_access_token"

YOOMONEY_WALLET_ID = "wallet_number"
YOOMONEY_ACCESS_TOKEN = "yoomoney_token"
YOOMONEY_NOTIFICATION_SECRET = "notification_secret"
```

4. **Launch the bot**
```bash
python app.py
```

## 🔐 Security

- All tokens and keys are stored in a separate configuration file
- Access control checks for admin commands
- Middleware for managing database sessions
- SQL injection protection via ORM

## 📝 License

MIT License

## 👨‍💻 Development

### Development Requirements
- Python 3.10+
- Understanding of asyncio
- Knowledge of aiogram 3.x
- Experience with SQLAlchemy
