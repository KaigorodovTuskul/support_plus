# 🚀 Платформа "Опора" - Полное руководство по деплою

## 📋 Содержание

1. [О проекте](#о-проекте)
2. [Быстрый старт](#быстрый-старт)
3. [Деплой на VPS](#деплой-на-vps)
4. [Документация](#документация)

---

## О проекте

**Опора** - веб-платформа для доступа к государственным льготам и коммерческим предложениям для пенсионеров, инвалидов, многодетных семей и других льготных категорий граждан.

### Основные функции:

✅ **Для граждан:**
- Просмотр доступных льгот
- Регистрация как льготник
- Пожертвования проекту
- Просмотр предложений от бизнеса

✅ **Для бизнеса:**
- Регистрация как компания/ИП/самозанятый
- Создание акций и специальных предложений
- Управление своими предложениями
- Статистика просмотров и кликов

### Технологический стек:

**Backend:**
- Django 5.0
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Swagger API Documentation

**Frontend:**
- Nuxt.js 3
- Vue.js 3
- Tailwind CSS

---

## Быстрый старт

### Локальная разработка

#### Backend

```bash
cd backend

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл
cp .env.example .env
# Отредактируйте .env с вашими настройками

# Запустите миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Запустите сервер
python manage.py runserver
```

Откройте: http://localhost:8000/admin

#### Frontend

```bash
cd frontend

# Установите зависимости
npm install

# Создайте .env файл
cp .env.example .env

# Запустите dev сервер
npm run dev
```

Откройте: http://localhost:3000

---

## Деплой на VPS

У вас есть три подробных руководства:

### 1. 📋 [PRE_DEPLOY_TEST.md](./PRE_DEPLOY_TEST.md)
**Читайте ПЕРВЫМ!**

Проверьте готовность проекта перед деплоем:
- Тестирование локально
- Проверка настроек
- Создание .env.example
- Подготовка git репозитория
- Чеклист готовности

### 2. ✅ [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
**Быстрое руководство (30-40 минут)**

Пошаговый чеклист для быстрого деплоя:
- Подготовка сервера (5-10 мин)
- PostgreSQL (2-3 мин)
- Backend (5-7 мин)
- Frontend (3-5 мин)
- Nginx (2-3 мин)
- SSL сертификат (2 мин)

### 3. 📚 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
**Подробное руководство с объяснениями**

Полная документация со всеми деталями:
- Детальные инструкции
- Troubleshooting
- Настройка бэкапов
- Мониторинг
- Безопасность

---

## Структура проекта

```
hacktheice/
├── backend/                  # Django бэкенд
│   ├── config/              # Настройки Django
│   ├── users/               # Пользователи
│   ├── benefits/            # Льготы
│   ├── donations/           # Пожертвования
│   ├── business_offers/     # Предложения от бизнеса (НОВОЕ)
│   ├── chatbot/             # AI Чатбот
│   ├── search/              # Поиск
│   └── manage.py
│
├── frontend/                # Nuxt.js фронтенд
│   ├── pages/
│   │   ├── index.vue       # Главная
│   │   ├── register.vue    # Регистрация (обновлена)
│   │   ├── donate/         # Пожертвования
│   │   │   ├── individual.vue
│   │   │   ├── corporate.vue
│   │   │   ├── payment.vue (исправлена)
│   │   │   └── leaderboard.vue
│   │   └── business/       # Раздел для бизнеса (НОВОЕ)
│   │       ├── index.vue
│   │       ├── my-offers.vue
│   │       └── create.vue
│   ├── components/
│   └── nuxt.config.ts
│
├── DEPLOYMENT_GUIDE.md      # Подробное руководство
├── DEPLOYMENT_CHECKLIST.md  # Быстрый чеклист
├── PRE_DEPLOY_TEST.md       # Тестирование перед деплоем
└── README_DEPLOYMENT.md     # Этот файл
```

---

## API Endpoints

### Пользователи
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход
- `POST /api/auth/refresh/` - Обновление токена

### Льготы
- `GET /api/benefits/` - Список льгот
- `GET /api/benefits/{id}/` - Детали льготы

### Пожертвования
- `POST /api/donations/` - Создать донат
- `GET /api/donations/by_transaction/?transaction_id=XXX` - Получить донат по ID (НОВОЕ)
- `POST /api/donations/confirm_payment/` - Подтвердить оплату
- `GET /api/donations/leaderboard/` - Лидерборд
- `GET /api/donations/stats/` - Статистика

### Предложения от бизнеса (НОВОЕ)
- `GET /api/business/offers/` - Список предложений
- `GET /api/business/offers/active/` - Активные предложения
- `POST /api/business/offers/` - Создать предложение (требует авторизации)
- `GET /api/business/offers/{id}/` - Детали предложения
- `POST /api/business/offers/{id}/track_view/` - Отследить просмотр
- `POST /api/business/offers/{id}/track_click/` - Отследить клик

Полная документация: https://your-domain.com/swagger

---

## Последние изменения (что было исправлено)

### ✅ Исправлены критические баги с пожертвованиями:

1. **Проблема:** Сумма отображалась как 1000 вместо реальной на странице оплаты
   - **Решение:** Добавлен `const config = useRuntimeConfig()` в payment.vue
   - Добавлен endpoint `/api/donations/by_transaction/`
   - Передача суммы через query параметр

2. **Проблема:** Ошибка "config is not defined" при нажатии "Оплачено"
   - **Решение:** Исправлена инициализация config

3. **Проблема:** Ошибка "Транзакция не найдена"
   - **Решение:** Добавлен новый API endpoint для получения доната по transaction_id

### ✅ Добавлена регистрация для бизнеса:

- Выбор типа пользователя при регистрации
- Отдельные поля для физ. лиц и бизнеса
- Поддержка компаний, ИП, самозанятых

### ✅ Создан раздел "Бизнесу":

- Просмотр акций от бизнеса
- Создание и управление акциями
- Модерация предложений
- Статистика просмотров и кликов

---

## Переменные окружения

### Backend (.env)

```env
# Django
SECRET_KEY=your_secret_key_change_this
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_NAME=opora_db
DATABASE_USER=opora_user
DATABASE_PASSWORD=strong_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

### Frontend (.env)

```env
NUXT_PUBLIC_API_BASE=https://your-domain.com/api
```

---

## Полезные команды

### Backend

```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Собрать статику
python manage.py collectstatic

# Запуск dev сервера
python manage.py runserver

# Django shell
python manage.py shell
```

### Frontend

```bash
# Dev сервер
npm run dev

# Production build
npm run build

# Preview production
npm run preview

# Lint
npm run lint
```

### На сервере (после деплоя)

```bash
# Перезапуск backend
sudo systemctl restart gunicorn

# Перезапуск frontend
pm2 restart opora-frontend

# Перезапуск nginx
sudo systemctl restart nginx

# Логи backend
sudo journalctl -u gunicorn -f

# Логи frontend
pm2 logs opora-frontend

# Бэкап БД
sudo -u postgres pg_dump opora_db > backup.sql

# Обновление проекта
./deploy.sh
```

---

## Безопасность

### ⚠️ ВАЖНО перед деплоем:

1. **Измените SECRET_KEY** в backend/.env
2. **Установите DEBUG=False** в продакшене
3. **Используйте сильные пароли** для:
   - PostgreSQL пользователя
   - Django суперпользователя
   - SSH доступа

4. **Настройте ALLOWED_HOSTS** с вашим доменом
5. **Настройте CORS_ALLOWED_ORIGINS** с вашим доменом
6. **Настройте CSRF_TRUSTED_ORIGINS** с вашим доменом

### Рекомендации:

- Регулярно обновляйте зависимости
- Настройте автоматические бэкапы БД
- Используйте fail2ban для защиты от брутфорса
- Настройте мониторинг сервера
- Регулярно проверяйте логи на ошибки

---

## Мониторинг и обслуживание

### Проверка статуса сервисов

```bash
# Все сервисы
sudo systemctl status gunicorn nginx postgresql
pm2 status

# Использование диска
df -h

# Использование памяти
free -h

# Нагрузка на процессор
htop
```

### Логи

```bash
# Backend
sudo journalctl -u gunicorn --since "1 hour ago"

# Frontend
pm2 logs opora-frontend --lines 100

# Nginx access
sudo tail -f /var/log/nginx/access.log

# Nginx errors
sudo tail -f /var/log/nginx/error.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Бэкапы

```bash
# Создать бэкап БД
sudo -u postgres pg_dump opora_db > backup_$(date +%Y%m%d).sql

# Восстановить БД
sudo -u postgres psql opora_db < backup_20240123.sql

# Бэкап медиа файлов
tar -czf media_backup.tar.gz /var/www/opora/backend/media/
```

---

## Troubleshooting

### 502 Bad Gateway

```bash
# Проверьте gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50

# Проверьте socket
ls -la /var/www/opora/backend/gunicorn.sock
```

### Frontend не запускается

```bash
# Проверьте логи
pm2 logs opora-frontend

# Пересоберите
cd /var/www/opora/frontend
npm run build
pm2 restart opora-frontend
```

### База данных недоступна

```bash
# Проверьте PostgreSQL
sudo systemctl status postgresql

# Проверьте подключение
sudo -u postgres psql -d opora_db
```

---

## Поддержка

### Документация

- [Django](https://docs.djangoproject.com/)
- [Nuxt.js](https://nuxt.com/docs)
- [Nginx](https://nginx.org/ru/docs/)
- [Let's Encrypt](https://letsencrypt.org/docs/)

### Полезные ссылки

- Swagger API: https://your-domain.com/swagger
- Django Admin: https://your-domain.com/admin
- SSL тест: https://www.ssllabs.com/ssltest/

---

## Лицензия

Проект разработан для хакатона "Hack the Ice 2024"

---

## Авторы

Команда разработчиков "Опора"

---

## Changelog

### v2.0 (Текущая версия)
- ✅ Исправлены баги с пожертвованиями
- ✅ Добавлена регистрация для бизнеса
- ✅ Создан раздел "Бизнесу" с акциями
- ✅ Добавлен endpoint `by_transaction` для донатов
- ✅ Улучшена обработка сумм в пожертвованиях
- ✅ Добавлена модель BusinessOffer
- ✅ Создан функционал управления акциями
- ✅ Добавлена статистика просмотров и кликов

### v1.0
- Базовый функционал льгот
- Регистрация пользователей
- Пожертвования
- Chatbot интеграция

---

**Готовы к деплою? Начните с [PRE_DEPLOY_TEST.md](./PRE_DEPLOY_TEST.md)! 🚀**
