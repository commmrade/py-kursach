# API для математических расчётов — Калькулятор формул, графики функций

Это асинхронное FastAPI-приложение предоставляет API для хранения математических формул пользователей, вычисления выражений с помощью SymPy и построения графиков функций с Matplotlib. Поддерживается аутентификация через JWT, валидация через Pydantic и асинхронная работа с SQLite (через SQLAlchemy и aiosqlite). Проект соответствует минимальным требованиям: CRUD для сущности "формула", обработка ошибок, документация, структура кода и интеграция с БД.

## Зависимости

Установите зависимости из `requirements.txt` (обновлён для совместимости с Python 3.13+):

```
fastapi>=0.112.0
uvicorn==0.24.0
sqlalchemy>=2.0.31
aiosqlite==0.19.0
pydantic>=2.8.0
passlib[bcrypt]==1.7.4
pyjwt==2.8.0
matplotlib==3.8.2
sympy==1.12
```

Установка:
```
pip install -r requirements.txt
```

## Структура проекта

- `database.py`: Настройка асинхронной БД (SQLite).
- `models.py`: ORM-модели (User, Formula).
- `schemas.py`: Pydantic-схемы для валидации.
- `auth.py`: JWT-аутентификация и хэширование (bcrypt).
- `maths.py`: Асинхронные CRUD-операции для формул.
- `main.py`: FastAPI-приложение с эндпоинтами.
- `requirements.txt`: Зависимости.
- `README.md`: Эта инструкция.

## Запуск локально

1. **Подготовка**:
   - Убедитесь, что установлен Python 3.10+ (рекомендуется 3.13 для теста совместимости).
   - Создайте виртуальное окружение (опционально):
     ```
     python -m venv venv
     source venv/bin/activate  # Linux/Mac
     # или venv\Scripts\activate  # Windows
     ```
   - Установите зависимости: `pip install -r requirements.txt`.

2. **Настройка**:
   - Измените `SECRET_KEY` в `auth.py` на безопасное значение (например, сгенерируйте: `python -c "import secrets; print(secrets.token_hex(32))"`).
   - База данных (`test.db`) создастся автоматически при первом запуске.

3. **Запуск сервера**:
   ```
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
   - `--reload`: Автоперезагрузка при изменениях кода (для разработки).
   - Сервер доступен по `http://127.0.0.1:8000`.

4. **Документация**:
   - Откройте в браузере: `http://127.0.0.1:8000/docs` (Swagger UI для интерактивного тестирования эндпоинтов).
   - Или `http://127.0.0.1:8000/redoc` для ReDoc.

## Использование API

### 1. Регистрация
- **Метод**: POST `/register`
- **Тело** (JSON):
  ```
  {
    "username": "user1",
    "password": "pass123"  # Макс. 72 символа.
  }
  ```
- Пример curl:
  ```
  curl -X POST "http://127.0.0.1:8000/register" -H "Content-Type: application/json" -d '{"username": "user1", "password": "pass123"}'
  ```
- Ответ: `{"msg": "User registered"}`

### 2. Логин
- **Метод**: POST `/login`
- **Тело** (form-data: username=user1, password=pass123)
- Пример curl:
  ```
  curl -X POST "http://127.0.0.1:8000/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=user1&password=pass123"
  ```
- Ответ: `{"access_token": "eyJ...", "token_type": "bearer"}` (скопируйте токен).

### 3. CRUD для формул (защищено: Authorization: Bearer <token>)
- **Создание** (POST `/formulas/`):
  ```
  curl -X POST "http://127.0.0.1:8000/formulas/" -H "Authorization: Bearer your_token" -H "Content-Type: application/json" -d '{"formula_string": "2*x + 3", "description": "Линейная"}'
  ```
- **Получение всех** (GET `/formulas/`):
  ```
  curl -X GET "http://127.0.0.1:8000/formulas/" -H "Authorization: Bearer your_token"
  ```
- **Получение одной** (GET `/formulas/1`): Замените 1 на ID.
- **Обновление** (PUT `/formulas/1`): Аналогично созданию.
- **Удаление** (DELETE `/formulas/1`).

### 4. Вычисление (открыто: POST `/calculate/`)
```
curl -X POST "http://127.0.0.1:8000/calculate/" -H "Content-Type: application/json" -d '{"formula": "2 + 2*3"}'
```
- Ответ: `{"result": "8"}`

### 5. График (открыто: POST `/plot/`)
```
curl -X POST "http://127.0.0.1:8000/plot/" -H "Content-Type: application/json" -d '{"function": "x**2", "x_min": -5, "x_max": 5}'
```
- Ответ: `{"image": "base64_string"}` (декодируйте в PNG для просмотра).

## Обработка ошибок
- 400: Username уже существует.
- 401: Неверные credentials.
- 404: Формула не найдена.
- 422: Неверные данные (валидация) или формула.