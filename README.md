# Local LLM Telegram Bot

Бот для Telegram, який веде живий діалог з локальною LLM через **Ollama**.

## Вимоги

- Python 3.11+
- [Ollama](https://ollama.com) (встановлений та запущений локально)
- Telegram Bot Token (від [@BotFather](https://t.me/BotFather))

## Встановлення

```bash
# 1. Клонувати репозиторій
# 2. Створити віртуальне оточення
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Встановити залежності
pip install -r requirements.txt

# 4. Налаштувати .env
cp .env.example .env
# Відредагувати .env — вставити BOT_TOKEN

# 5. Запустити Ollama та завантажити модель
ollama pull llama3.2

# 6. Запустити бота
python src/main.py
```

## Архітектура проєкту

```
src/
├── main.py                 # Точка входу
├── config.py               # Налаштування (pydantic-settings)
├── bot/
│   ├── __init__.py
│   ├── handlers.py         # Хендлери команд та повідомлень
│   ├── keyboards.py        # Клавіатури (Inline / Reply)
│   ├── middlewares.py      # Middlewares (тротлінг, логування)
│   └── filters.py          # Кастомні фільтри
├── llm/
│   ├── __init__.py
│   ├── base.py             # Абстрактний інтерфейс LLM
│   ├── ollama_client.py    # Реалізація через Ollama API
│   └── service.py          # Сервіс генерації відповіді
├── services/
│   ├── __init__.py
│   └── chat_service.py     # Управління сесіями діалогів
└── utils/
    ├── __init__.py
    └── helpers.py          # Допоміжні функції
```
