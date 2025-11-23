# 🚀 Руководство по деплою проекта на VPS

## Предварительные требования

- VPS сервер (Ubuntu 20.04/22.04 или Debian)
- Доменное имя (например, `opora.ru`)
- SSH доступ к серверу
- Root права или sudo доступ

## Шаг 1: Подготовка сервера

### 1.1 Подключитесь к серверу

```bash
ssh root@your-server-ip
# или
ssh username@your-server-ip
```

### 1.2 Обновите систему

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Установите необходимые пакеты

```bash
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx postgresql postgresql-contrib curl
```

### 1.4 Установите Node.js и npm

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Проверьте установку:
```bash
node --version  # должно быть v20.x.x
npm --version
```

### 1.5 Установите PM2 (менеджер процессов для Node.js)

```bash
sudo npm install -g pm2
```

## Шаг 2: Настройка PostgreSQL

### 2.1 Создайте базу данных и пользователя

```bash
sudo -u postgres psql
```

В консоли PostgreSQL выполните:

```sql
CREATE DATABASE opora_db;
CREATE USER opora_user WITH PASSWORD 'your_strong_password_here';
ALTER ROLE opora_user SET client_encoding TO 'utf8';
ALTER ROLE opora_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE opora_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE opora_db TO opora_user;
\q
```

## Шаг 3: Клонирование и настройка проекта

### 3.1 Создайте директорию для проекта

```bash
sudo mkdir -p /var/www/opora
sudo chown $USER:$USER /var/www/opora
cd /var/www/opora
```

### 3.2 Клонируйте репозиторий

```bash
git clone https://github.com/your-username/hacktheice.git .
# или загрузите файлы через scp/sftp
```

## Шаг 4: Настройка Backend (Django)

### 4.1 Создайте виртуальное окружение

```bash
cd /var/www/opora/backend
python3 -m venv venv
source venv/bin/activate
```

### 4.2 Установите зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 4.3 Создайте .env файл

```bash
nano /var/www/opora/backend/.env
```

Добавьте следующее содержимое:

```env
# Django settings
SECRET_KEY=your_very_secret_key_here_change_this_in_production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# Database
DATABASE_NAME=opora_db
DATABASE_USER=opora_user
DATABASE_PASSWORD=your_strong_password_here
DATABASE_HOST=localhost
DATABASE_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 4.4 Обновите settings.py для продакшена

```bash
nano /var/www/opora/backend/config/settings.py
```

Добавьте в начало файла:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# ... существующий код ...

# В раздел DATABASES измените на:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'opora_db'),
        'USER': os.getenv('DATABASE_USER', 'opora_user'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# Добавьте после ALLOWED_HOSTS:
CSRF_TRUSTED_ORIGINS = [
    'https://your-domain.com',
    'https://www.your-domain.com',
]

# В конец файла добавьте:
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

Не забудьте установить python-dotenv:
```bash
pip install python-dotenv
```

### 4.5 Выполните миграции и соберите статику

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4.6 Создайте суперпользователя

```bash
python manage.py createsuperuser
```

### 4.7 Создайте systemd сервис для Gunicorn

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Добавьте:

```ini
[Unit]
Description=gunicorn daemon for Opora Django app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/opora/backend
Environment="PATH=/var/www/opora/backend/venv/bin"
ExecStart=/var/www/opora/backend/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/opora/backend/gunicorn.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Установите права:

```bash
sudo chown -R www-data:www-data /var/www/opora
sudo chmod -R 755 /var/www/opora
```

Запустите и включите сервис:

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## Шаг 5: Настройка Frontend (Nuxt.js)

### 5.1 Установите зависимости

```bash
cd /var/www/opora/frontend
npm install
```

### 5.2 Создайте .env файл

```bash
nano /var/www/opora/frontend/.env
```

Добавьте:

```env
NUXT_PUBLIC_API_BASE=https://your-domain.com/api
```

### 5.3 Соберите продакшн версию

```bash
npm run build
```

### 5.4 Запустите с PM2

```bash
pm2 start npm --name "opora-frontend" -- start
pm2 save
pm2 startup
```

Выполните команду, которую выдаст `pm2 startup`.

## Шаг 6: Настройка Nginx

### 6.1 Создайте конфигурацию Nginx

```bash
sudo nano /etc/nginx/sites-available/opora
```

Добавьте следующую конфигурацию:

```nginx
# Перенаправление с www на без www
server {
    listen 80;
    server_name www.your-domain.com;
    return 301 $scheme://your-domain.com$request_uri;
}

# Основной сервер
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    # Frontend (Nuxt.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API (Django)
    location /api {
        proxy_pass http://unix:/var/www/opora/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin {
        proxy_pass http://unix:/var/www/opora/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Swagger
    location /swagger {
        proxy_pass http://unix:/var/www/opora/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://unix:/var/www/opora/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django static files
    location /static/ {
        alias /var/www/opora/backend/staticfiles/;
    }

    # Django media files
    location /media/ {
        alias /var/www/opora/backend/media/;
    }
}
```

**Замените `your-domain.com` на ваш реальный домен!**

### 6.2 Активируйте конфигурацию

```bash
sudo ln -s /etc/nginx/sites-available/opora /etc/nginx/sites-enabled/
sudo nginx -t  # Проверка конфигурации
sudo systemctl restart nginx
```

## Шаг 7: Настройка SSL с Let's Encrypt

### 7.1 Убедитесь, что домен указывает на ваш сервер

Проверьте DNS записи:
```bash
nslookup your-domain.com
```

Должен вернуть IP вашего сервера.

### 7.2 Получите SSL сертификат

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Следуйте инструкциям:
1. Введите email для уведомлений
2. Согласитесь с Terms of Service
3. Выберите перенаправление HTTP на HTTPS (опция 2)

Certbot автоматически обновит конфигурацию Nginx и добавит SSL.

### 7.3 Проверьте автоматическое обновление сертификата

```bash
sudo certbot renew --dry-run
```

Если всё ОК, сертификат будет автоматически обновляться.

### 7.4 Настройте автоматическое обновление

Certbot уже создал cron задачу, но можно проверить:

```bash
sudo systemctl status certbot.timer
```

## Шаг 8: Настройка Firewall

### 8.1 Установите UFW (если не установлен)

```bash
sudo apt install ufw
```

### 8.2 Настройте правила

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

## Шаг 9: Финальная проверка

### 9.1 Проверьте все сервисы

```bash
# Backend
sudo systemctl status gunicorn

# Frontend
pm2 status

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql
```

### 9.2 Проверьте логи при ошибках

```bash
# Gunicorn
sudo journalctl -u gunicorn -n 50

# PM2
pm2 logs opora-frontend

# Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 9.3 Откройте в браузере

- `https://your-domain.com` - главная страница (должна открыться по HTTPS)
- `https://your-domain.com/admin` - Django админка
- `https://your-domain.com/swagger` - API документация

## Шаг 10: Обновление проекта

Создайте скрипт для обновления:

```bash
nano /var/www/opora/deploy.sh
```

Добавьте:

```bash
#!/bin/bash

echo "🚀 Starting deployment..."

# Backend
cd /var/www/opora/backend
source venv/bin/activate
git pull origin master
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
echo "✅ Backend updated"

# Frontend
cd /var/www/opora/frontend
git pull origin master
npm install
npm run build
pm2 restart opora-frontend
echo "✅ Frontend updated"

echo "🎉 Deployment complete!"
```

Сделайте скрипт исполняемым:

```bash
chmod +x /var/www/opora/deploy.sh
```

Для обновления просто запускайте:

```bash
cd /var/www/opora
./deploy.sh
```

## Полезные команды

### Backend (Django)

```bash
# Перезапуск
sudo systemctl restart gunicorn

# Просмотр логов
sudo journalctl -u gunicorn -f

# Выполнение команд Django
cd /var/www/opora/backend
source venv/bin/activate
python manage.py shell
python manage.py createsuperuser
```

### Frontend (Nuxt.js)

```bash
# Перезапуск
pm2 restart opora-frontend

# Логи
pm2 logs opora-frontend

# Статус
pm2 status
```

### Nginx

```bash
# Перезапуск
sudo systemctl restart nginx

# Проверка конфигурации
sudo nginx -t

# Логи
sudo tail -f /var/log/nginx/error.log
```

### SSL сертификат

```bash
# Проверка сертификата
sudo certbot certificates

# Принудительное обновление
sudo certbot renew

# Тест обновления
sudo certbot renew --dry-run
```

## Troubleshooting

### Проблема: 502 Bad Gateway

**Решение:**
```bash
# Проверьте gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50

# Проверьте socket
ls -la /var/www/opora/backend/gunicorn.sock

# Проверьте права
sudo chown -R www-data:www-data /var/www/opora
```

### Проблема: Static files не загружаются

**Решение:**
```bash
cd /var/www/opora/backend
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Проблема: Frontend не работает

**Решение:**
```bash
pm2 logs opora-frontend
pm2 restart opora-frontend

# Если не помогло, пересоберите
cd /var/www/opora/frontend
npm run build
pm2 restart opora-frontend
```

### Проблема: Database connection refused

**Решение:**
```bash
# Проверьте PostgreSQL
sudo systemctl status postgresql

# Проверьте подключение
sudo -u postgres psql -d opora_db

# Проверьте .env файл
cat /var/www/opora/backend/.env
```

## Безопасность

### Измените пароли по умолчанию

1. PostgreSQL пароль
2. Django SECRET_KEY
3. Пароль суперпользователя Django

### Настройте регулярные бэкапы

```bash
# Создайте скрипт бэкапа
nano /var/www/opora/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/opora"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап базы данных
sudo -u postgres pg_dump opora_db > $BACKUP_DIR/db_$DATE.sql

# Бэкап медиа файлов
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/opora/backend/media/

# Удалить бэкапы старше 7 дней
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /var/www/opora/backup.sh
```

Добавьте в cron (запуск каждый день в 2:00):

```bash
sudo crontab -e
```

Добавьте строку:
```
0 2 * * * /var/www/opora/backup.sh
```

## Мониторинг

### Установите monitoring (опционально)

```bash
# Установите netdata для мониторинга
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Доступ: http://your-server-ip:19999
```

---

## 🎉 Готово!

Ваш проект теперь работает на:
- **https://your-domain.com** - основной сайт с SSL
- **https://your-domain.com/admin** - админка Django
- **https://your-domain.com/swagger** - API документация

Не забудьте заменить `your-domain.com` на ваш реальный домен во всех конфигурационных файлах!
