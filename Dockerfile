# Вибираємо базовий образ
FROM python:3.13-slim

# Встановлюємо необхідні системні пакети для Poetry та компіляції залежностей
RUN apt-get update && apt-get install -y gcc curl

# Встановлюємо Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Додаємо Poetry до PATH
ENV PATH="/root/.local/bin:$PATH"

# Створюємо та переміщаємося до робочої директорії
WORKDIR /src

# Копіюємо файли проєкту до контейнера
COPY . /src

# Встановлюємо залежності через Poetry
RUN poetry install --no-interaction --no-dev

# Відкриваємо порт, який буде використовувати додаток
EXPOSE 8000

# Запускаємо сервер
CMD ["python3", "main.py"]
