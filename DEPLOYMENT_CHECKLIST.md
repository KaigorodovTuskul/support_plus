# ✅ Чеклист для деплоя

## Перед началом

- [ ] VPS сервер с Ubuntu 20.04+ готов
- [ ] Есть доступ по SSH
- [ ] Домен настроен и DNS указывает на IP сервера
- [ ] Есть root/sudo права

## 1. Подготовка сервера (5-10 минут)

```bash
# Подключитесь к серверу
ssh root@your-server-ip

# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите всё необходимое
sudo apt install -y python3 python3-pip python3-venv git nginx certbot \
  python3-certbot-nginx postgresql postgresql-contrib curl

# Установите Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Установите PM2
sudo npm install -g pm2
```

## 2. PostgreSQL (2-3 минуты)

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE opora_db;
CREATE USER opora_user WITH PASSWORD 'ПРИДУМАЙТЕ_СЛОЖНЫЙ_ПАРОЛЬ';
GRANT ALL PRIVILEGES ON DATABASE opora_db TO opora_user;
\q
```

## 3. Клонирование проекта (1-2 минуты)

```bash
sudo mkdir -p /var/www/opora
sudo chown $USER:$USER /var/www/opora
cd /var/www/opora

# Загрузите проект (git или scp)
git clone YOUR_REPO_URL .
# ИЛИ загрузите через FileZilla/WinSCP
```

## 4. Backend настройка (5-7 минут)

```bash
cd /var/www/opora/backend

# Создайте venv и установите пакеты
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary python-dotenv
```

Создайте `.env`:
```bash
nano .env
```

```env
SECRET_KEY=ПРИДУМАЙТЕ_СЛУЧАЙНУЮ_СТРОКУ_50_СИМВОЛОВ
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

DATABASE_NAME=opora_db
DATABASE_USER=opora_user
DATABASE_PASSWORD=ВАШ_ПАРОЛЬ_ИЗ_ШАГА_2
DATABASE_HOST=localhost
DATABASE_PORT=5432

CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

Обновите `config/settings.py` (добавьте в начало):
```python
from dotenv import load_dotenv
import os

load_dotenv()
```

Найдите секцию DATABASES и замените на:
```python
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
```

Добавьте в конец:
```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
CSRF_TRUSTED_ORIGINS = [
    'https://your-domain.com',
    'https://www.your-domain.com',
]
```

Запустите миграции:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # Создайте админа
```

## 5. Gunicorn systemd сервис (3-4 минуты)

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Вставьте:
```ini
[Unit]
Description=gunicorn daemon
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

```bash
sudo chown -R www-data:www-data /var/www/opora
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 6. Frontend настройка (3-5 минут)

```bash
cd /var/www/opora/frontend

# Создайте .env
nano .env
```

```env
NUXT_PUBLIC_API_BASE=https://your-domain.com/api
```

```bash
npm install
npm run build

# Запустите с PM2
pm2 start npm --name "opora-frontend" -- start
pm2 save
pm2 startup  # Выполните команду, которую выдаст эта команда
```

## 7. Nginx конфигурация (2-3 минуты)

```bash
sudo nano /etc/nginx/sites-available/opora
```

Вставьте (ЗАМЕНИТЕ `your-domain.com` на ваш домен!):

```nginx
server {
    listen 80;
    server_name www.your-domain.com;
    return 301 $scheme://your-domain.com$request_uri;
}

server {
    listen 80;
    server_name your-domain.com;
    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location ~ ^/(api|admin|swagger|redoc) {
        proxy_pass http://unix:/var/www/opora/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/opora/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/opora/backend/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/opora /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 8. SSL сертификат (2 минуты)

```bash
# Убедитесь что домен указывает на сервер
nslookup your-domain.com

# Получите SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Следуйте инструкциям certbot, выберите опцию "2" для редиректа на HTTPS.

## 9. Firewall (1 минута)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 10. Проверка (1 минута)

```bash
# Проверьте все сервисы
sudo systemctl status gunicorn
pm2 status
sudo systemctl status nginx

# Откройте в браузере
https://your-domain.com
https://your-domain.com/admin
```

## 🎉 Готово!

---

## Быстрое обновление проекта

Создайте скрипт:
```bash
nano /var/www/opora/deploy.sh
```

```bash
#!/bin/bash
cd /var/www/opora/backend
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn

cd /var/www/opora/frontend
git pull
npm install
npm run build
pm2 restart opora-frontend
```

```bash
chmod +x /var/www/opora/deploy.sh
```

Теперь для обновления просто:
```bash
./deploy.sh
```

---

## Важные команды

### Перезапуск сервисов
```bash
sudo systemctl restart gunicorn  # Backend
pm2 restart opora-frontend       # Frontend
sudo systemctl restart nginx     # Nginx
```

### Логи
```bash
sudo journalctl -u gunicorn -f  # Backend логи
pm2 logs opora-frontend         # Frontend логи
sudo tail -f /var/log/nginx/error.log  # Nginx ошибки
```

### Бэкап БД
```bash
sudo -u postgres pg_dump opora_db > backup_$(date +%Y%m%d).sql
```

### Восстановление БД
```bash
sudo -u postgres psql opora_db < backup_20240123.sql
```

---

## Замените во ВСЕХ файлах конфигурации:

- `your-domain.com` → ваш реальный домен
- `your-server-ip` → IP вашего сервера
- `YOUR_REPO_URL` → URL вашего git репозитория
- Пароли и секретные ключи

## Полезные ссылки

- Django admin: https://your-domain.com/admin
- API Swagger: https://your-domain.com/swagger
- SSL проверка: https://www.ssllabs.com/ssltest/
