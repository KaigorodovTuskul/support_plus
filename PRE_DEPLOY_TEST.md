# 🧪 Тестирование перед деплоем

Проверьте всё локально перед отправкой на сервер!

## 1. Backend тесты

```bash
cd backend

# Активируйте venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Проверьте миграции
python manage.py makemigrations --check --dry-run
python manage.py migrate --check

# Соберите статику
python manage.py collectstatic --noinput --dry-run

# Запустите сервер
python manage.py runserver
```

Проверьте в браузере:
- [ ] http://localhost:8000/admin - админка открывается
- [ ] http://localhost:8000/swagger - API документация работает
- [ ] http://localhost:8000/api/benefits/ - API возвращает данные

## 2. Frontend тесты

```bash
cd frontend

# Проверьте сборку
npm run build

# Запустите продакшн версию локально
npm run preview
```

Проверьте в браузере:
- [ ] http://localhost:3000 - главная страница
- [ ] http://localhost:3000/register - регистрация работает
- [ ] http://localhost:3000/business - раздел бизнесу
- [ ] http://localhost:3000/donate/individual - пожертвования

## 3. Проверка настроек для продакшена

### Backend: config/settings.py

Убедитесь что есть:
```python
from dotenv import load_dotenv
import os

load_dotenv()

# ...

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

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

CSRF_TRUSTED_ORIGINS = [
    'https://your-domain.com',
    'https://www.your-domain.com',
]
```

### Frontend: nuxt.config.ts

Убедитесь что API базовый URL читается из env:
```typescript
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api'
    }
  }
})
```

## 4. Создайте .env.example файлы

### Backend: .env.example

```bash
cd backend
cat > .env.example << 'EOF'
# Django settings
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost

# Database
DATABASE_NAME=opora_db
DATABASE_USER=opora_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
EOF
```

### Frontend: .env.example

```bash
cd frontend
cat > .env.example << 'EOF'
NUXT_PUBLIC_API_BASE=https://your-domain.com/api
EOF
```

## 5. Подготовьте git репозиторий

```bash
# Добавьте .gitignore если его нет
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
.pytest_cache/

# Django
*.log
db.sqlite3
db.sqlite3-journal
/staticfiles/
/media/

# Environment variables
.env
!.env.example

# Node.js
node_modules/
.nuxt/
.output/
dist/
.cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
backend/search_index.faiss
backend/search_mapping.json
EOF

# Коммит
git add .
git commit -m "Prepare for deployment"
git push origin master
```

## 6. Чеклист готовности к деплою

Перед началом деплоя убедитесь:

### Код
- [ ] Все изменения закоммичены в git
- [ ] Есть .env.example файлы
- [ ] requirements.txt актуален
- [ ] package.json актуален

### Настройки
- [ ] settings.py поддерживает переменные окружения
- [ ] DEBUG=False в продакшен .env
- [ ] ALLOWED_HOSTS содержит ваш домен
- [ ] CSRF_TRUSTED_ORIGINS настроен
- [ ] CORS_ALLOWED_ORIGINS настроен

### База данных
- [ ] Все миграции созданы
- [ ] Миграции применены локально успешно

### Frontend
- [ ] npm run build работает без ошибок
- [ ] API endpoint настроен через переменную окружения
- [ ] Все пути к API используют config.public.apiBase

### Сервер
- [ ] VPS сервер готов
- [ ] SSH доступ работает
- [ ] Домен указывает на IP сервера
- [ ] У вас есть все пароли (DB, суперпользователь Django)

## 7. Тестовые данные

Создайте несколько тестовых записей для проверки после деплоя:

```bash
cd backend
source venv/bin/activate
python manage.py shell
```

```python
from donations.models import Donation
from users.models import User

# Создайте тестовый донат
Donation.objects.create(
    donor_type='individual',
    donor_name='Тестовый донор',
    amount=5000,
    transaction_id='TEST-123',
    payment_status='paid',
    show_on_leaderboard=True
)

print("✅ Тестовые данные созданы")
```

## 8. Финальная проверка

### Запустите всё вместе локально

Терминал 1 (Backend):
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

Терминал 2 (Frontend):
```bash
cd frontend
npm run dev
```

### Проверьте все функции:

1. **Регистрация:**
   - [ ] Физ. лицо
   - [ ] Компания

2. **Пожертвования:**
   - [ ] Индивидуальное
   - [ ] Корпоративное
   - [ ] Leaderboard показывает донаты

3. **Бизнес раздел:**
   - [ ] Просмотр акций
   - [ ] Создание акции (после регистрации как бизнес)

4. **API:**
   - [ ] /api/benefits/
   - [ ] /api/donations/
   - [ ] /api/business/offers/

## 9. Сохраните важную информацию

Создайте файл с учётными данными (НЕ КОММИТЬТЕ ЕГО!):

```bash
cat > CREDENTIALS.txt << 'EOF'
# НЕ КОММИТИТЬ В GIT!

## VPS Server
IP:
SSH User:
SSH Password/Key:

## Domain
Domain: your-domain.com
DNS Provider:

## Database
DB Name: opora_db
DB User: opora_user
DB Password:

## Django
SECRET_KEY:
Superuser:
Superuser Password:

## SSL
Email for Let's Encrypt:

## Backup
Backup location: /var/backups/opora
EOF

# Добавьте в .gitignore
echo "CREDENTIALS.txt" >> .gitignore
```

## 🚀 Готовы к деплою!

Если все пункты выше ✅, можете переходить к DEPLOYMENT_CHECKLIST.md
