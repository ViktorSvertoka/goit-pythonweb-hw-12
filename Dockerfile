FROM python:3.13-slim

WORKDIR /app

# Оновлення системи та встановлення необхідних залежностей
RUN apt-get update && apt-get install -y \
        gcc g++ libc-dev libffi-dev libssl-dev \
    && pip install poetry \
    && poetry config virtualenvs.create false

# Копіювання файлів залежностей
COPY poetry.lock pyproject.toml /app/

# Встановлення залежностей
RUN poetry install --no-dev --no-interaction --no-ansi

# Копіювання всього коду
COPY . /app/

# Команда запуску
CMD ["python3", "main.py"]


