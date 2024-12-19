# Tickets servise

## Описание проекта

Этот сервис позволяет смотреть и сортировать мероприятия по названию, дате и наличию билетов. Данные берутся с сайта **quicktickets.ru**.

## Функциональность

- **Поиск билетов по дате:** Выберите дату на которую заплонировали свой поход в театр и выдаст все возможные представления в этот день.
- **Скрапинг данных:** Сервис автоматически собирает данные с сайта quicktickets.ru.
- **Хранение данных:** Используется база данных SQLite, которая сохраняет мероприятия между перезапусками сервиса.

## Как запустить проект

### Требования

- Git для работы с репозиторием.
- Установленный Docker и Docker Compose.

### Инструкции по запуску

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/vlad30071/CodeReview.git
cd your_project
```
2. **Запустите сервис:**
Выполните скрипт сборки и запуска:
```bash
./build.sh
```
3. **Откройте веб-приложение:** Перейдите в браузере по адресу https://localhost:5000. Выможете увидеть все ближайшие мероприятия и использовать функции сортировки, чтобы найти необходимые.

### Обновление данных (запуск скрапера вручную)
Если нужно обновить данные в базе, выполните следующую команду:
```bash
docker-compose exec web flask 
```

## Как работает проект
1. **Скрапинг:** Сервис использует модуль scraper.py для получения данных с сайта quicktickets.ru.
2. **Обработка данных:** Полученные рецепты сохраняются в базу данных SQLite.
3. **Интерфейс:** Пользователь вводит дату или название на веб-странице, а сервис ищет подходящие мероприятия в базе.
