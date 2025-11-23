# ⚡ Быстрые команды - Шпаргалка

## 🔐 SSH Подключение

```bash
ssh root@YOUR_SERVER_IP
# или
ssh username@YOUR_SERVER_IP
```

## 🔄 Перезапуск сервисов

```bash
# Backend (Django)
sudo systemctl restart gunicorn

# Frontend (Nuxt)
pm2 restart opora-frontend

# Nginx
sudo systemctl restart nginx

# PostgreSQL
sudo systemctl restart postgresql

# Всё сразу
sudo systemctl restart gunicorn nginx postgresql && pm2 restart opora-frontend
```

## 📊 Проверка статуса

```bash
# Backend
sudo systemctl status gunicorn

# Frontend
pm2 status

# Nginx
sudo systemctl status nginx

# База данных
sudo systemctl status postgresql

# Всё сразу
sudo systemctl status gunicorn nginx postgresql && pm2 status
```

## 📝 Просмотр логов

```bash
# Backend логи (последние 50 строк)
sudo journalctl -u gunicorn -n 50

# Backend логи (в реальном времени)
sudo journalctl -u gunicorn -f

# Frontend логи
pm2 logs opora-frontend

# Nginx errors
sudo tail -f /var/log/nginx/error.log

# Nginx access
sudo tail -f /var/log/nginx/access.log
```

## 🗄️ База данных

```bash
# Подключиться к БД
sudo -u postgres psql opora_db

# Бэкап
sudo -u postgres pg_dump opora_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление
sudo -u postgres psql opora_db < backup_20240123.sql

# Список всех БД
sudo -u postgres psql -l

# Создать бэкап в папке backups
sudo mkdir -p /var/backups/opora
sudo -u postgres pg_dump opora_db > /var/backups/opora/backup_$(date +%Y%m%d).sql
```

## 🔧 Django команды (на сервере)

```bash
# Перейти в папку проекта
cd /var/www/opora/backend

# Активировать venv
source venv/bin/activate

# Миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Собрать статику
python manage.py collectstatic --noinput

# Django shell
python manage.py shell

# Проверить миграции
python manage.py showmigrations
```

## 🚀 Обновление проекта

```bash
# Быстрое обновление (если есть deploy.sh)
cd /var/www/opora
./deploy.sh

# Ручное обновление - Backend
cd /var/www/opora/backend
source venv/bin/activate
git pull origin master
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn

# Ручное обновление - Frontend
cd /var/www/opora/frontend
git pull origin master
npm install
npm run build
pm2 restart opora-frontend

# Перезапустить Nginx
sudo systemctl restart nginx
```

## 🔒 SSL сертификат

```bash
# Проверить сертификат
sudo certbot certificates

# Обновить сертификат
sudo certbot renew

# Тест обновления (без реального обновления)
sudo certbot renew --dry-run

# Получить новый сертификат
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🔥 Firewall (UFW)

```bash
# Статус
sudo ufw status

# Разрешить HTTP/HTTPS
sudo ufw allow 'Nginx Full'

# Разрешить SSH
sudo ufw allow OpenSSH

# Включить
sudo ufw enable

# Отключить
sudo ufw disable
```

## 💾 Работа с файлами

```bash
# Скачать файл с сервера на локальный компьютер
scp username@server:/path/to/file /local/path

# Загрузить файл на сервер
scp /local/file username@server:/path/to/destination

# Скачать папку
scp -r username@server:/path/to/folder /local/path

# Загрузить папку
scp -r /local/folder username@server:/path/to/destination
```

## 📈 Мониторинг сервера

```bash
# Использование диска
df -h

# Использование памяти
free -h

# Топ процессов
htop
# или
top

# Нагрузка на систему
uptime

# Сетевые подключения
netstat -tulpn

# Процессы на портах
sudo lsof -i :80
sudo lsof -i :443
sudo lsof -i :3000
```

## 🧹 Очистка и обслуживание

```bash
# Очистить логи systemd (оставить последние 2 дня)
sudo journalctl --vacuum-time=2d

# Очистить apt кэш
sudo apt clean
sudo apt autoclean

# Удалить неиспользуемые пакеты
sudo apt autoremove

# Очистить старые PM2 логи
pm2 flush

# Найти большие файлы (больше 100MB)
sudo find / -type f -size +100M -exec ls -lh {} \;

# Использование диска по папкам
sudo du -sh /var/www/opora/*
```

## 🛠️ Исправление проблем

### 502 Bad Gateway

```bash
# 1. Проверить gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50

# 2. Проверить socket
ls -la /var/www/opora/backend/gunicorn.sock

# 3. Перезапустить
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 4. Проверить права
sudo chown -R www-data:www-data /var/www/opora
```

### Frontend не работает

```bash
# 1. Проверить логи
pm2 logs opora-frontend

# 2. Перезапустить
pm2 restart opora-frontend

# 3. Пересобрать
cd /var/www/opora/frontend
npm run build
pm2 restart opora-frontend

# 4. Проверить порт 3000
sudo lsof -i :3000
```

### База данных недоступна

```bash
# 1. Проверить статус
sudo systemctl status postgresql

# 2. Попробовать подключиться
sudo -u postgres psql opora_db

# 3. Перезапустить
sudo systemctl restart postgresql

# 4. Проверить настройки в .env
cat /var/www/opora/backend/.env
```

## 📦 PM2 команды

```bash
# Список процессов
pm2 list

# Логи
pm2 logs opora-frontend

# Перезапуск
pm2 restart opora-frontend

# Остановка
pm2 stop opora-frontend

# Запуск
pm2 start opora-frontend

# Удалить из PM2
pm2 delete opora-frontend

# Сохранить конфигурацию
pm2 save

# Информация о процессе
pm2 info opora-frontend

# Мониторинг
pm2 monit
```

## 🔐 Права доступа

```bash
# Установить владельца для всего проекта
sudo chown -R www-data:www-data /var/www/opora

# Установить права для папок
sudo find /var/www/opora -type d -exec chmod 755 {} \;

# Установить права для файлов
sudo find /var/www/opora -type f -exec chmod 644 {} \;

# Сделать файл исполняемым
chmod +x /var/www/opora/deploy.sh

# Проверить владельца
ls -la /var/www/opora/
```

## 🎯 Быстрые тесты

```bash
# Проверить доступность сайта
curl -I https://your-domain.com

# Проверить API
curl https://your-domain.com/api/benefits/

# Проверить SSL
curl -vI https://your-domain.com 2>&1 | grep -i ssl

# Проверить DNS
nslookup your-domain.com

# Проверить открытые порты
sudo netstat -tulpn | grep LISTEN
```

## 📞 Экстренные команды

```bash
# Если сайт не работает - перезапустить всё
sudo systemctl restart gunicorn nginx postgresql
pm2 restart all

# Если нет места на диске - очистить
sudo journalctl --vacuum-time=1d
sudo apt clean
pm2 flush

# Если слишком высокая нагрузка - проверить
htop
sudo systemctl restart gunicorn
pm2 restart all

# Если взломан - отключить сайт временно
sudo systemctl stop nginx

# Восстановить из бэкапа
sudo -u postgres psql opora_db < /var/backups/opora/backup_latest.sql
```

## 📱 Быстрые ссылки

После деплоя сохраните эти ссылки:

- 🌐 Сайт: https://your-domain.com
- 🔐 Админка: https://your-domain.com/admin
- 📚 API Docs: https://your-domain.com/swagger
- 📊 Redoc: https://your-domain.com/redoc

## 💡 Полезные алиасы

Добавьте в `~/.bashrc` для удобства:

```bash
# Добавить в ~/.bashrc
nano ~/.bashrc
```

```bash
# Алиасы для проекта Опора
alias opora-restart='sudo systemctl restart gunicorn nginx && pm2 restart opora-frontend'
alias opora-status='sudo systemctl status gunicorn nginx && pm2 status'
alias opora-logs='sudo journalctl -u gunicorn -f'
alias opora-backup='sudo -u postgres pg_dump opora_db > /var/backups/opora/backup_$(date +%Y%m%d).sql'
alias opora-update='cd /var/www/opora && ./deploy.sh'
alias opora-cd='cd /var/www/opora'
```

Затем:
```bash
source ~/.bashrc
```

Теперь можно использовать:
```bash
opora-restart  # Перезапустить всё
opora-status   # Проверить статус
opora-logs     # Посмотреть логи
opora-backup   # Сделать бэкап
opora-update   # Обновить проект
opora-cd       # Перейти в папку проекта
```

---

**Сохраните этот файл! Он пригодится для быстрого управления сервером.**
