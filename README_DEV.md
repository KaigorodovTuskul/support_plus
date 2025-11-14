# SUPPORT+ Development Guide

## Quick Start

### Backend (Django)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py create_mock_data
python manage.py createsuperuser --username admin --email admin@example.com
python manage.py runserver
```

Backend will be available at:
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

### Frontend (Nuxt 3)
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000/

## Current Status

### ✅ Completed
- **Backend (90%)**: Fully functional REST API with 11 benefits, 9 offers, authentication, search, filtering
- **Frontend (15%)**: Project setup, homepage created, Tailwind CSS configured

### 🔧 Known Issues
- **PWA Module**: Temporarily disabled on Windows due to path resolution issues. Will be re-enabled for production deployment on Linux/VPS.

### 📝 Next Steps
1. Create login/registration pages
2. Build dashboard with benefits list
3. Implement search and filter UI
4. Add accessibility settings panel
5. Integrate Web Speech API

## Features Implemented

### Backend API Endpoints
- `POST /api/auth/register/` - Register user
- `POST /api/auth/login/` - Login (JWT)
- `POST /api/auth/oauth/gosuslugi/` - Mock OAuth
- `GET /api/benefits/` - List benefits
- `GET /api/benefits/recommended/` - Personalized benefits
- `GET /api/benefits/dashboard/` - Dashboard data
- `GET /api/offers/` - Commercial offers
- `GET /api/profile/` - User profile
- `GET /api/export/benefits/pdf/` - Export to PDF

### Frontend Pages
- `/` - Homepage (completed)
- `/login` - Login page (TODO)
- `/register` - Registration page (TODO)
- `/dashboard` - User dashboard (TODO)
- `/benefits` - Benefits list (TODO)
- `/settings` - Accessibility settings (TODO)

## Database Content
- 11 Benefits (6 federal, 3 regional Yakutsk, 2 municipal Yakutsk)
- 9 Commercial offers
- 7 Categories (transport, medicine, utilities, social, housing, etc.)
- 5 Regions (including Yakutsk)

## Testing the API

### Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "password2": "test123",
    "beneficiary_category": "pensioner",
    "region": "Республика Саха (Якутия)"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

### Get Benefits (with token)
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/benefits/?personalized=true
```

## Technology Stack

### Backend
- Django 5.0
- Django REST Framework
- SQLite
- JWT Authentication
- BeautifulSoup (web scraping)
- ReportLab (PDF export)

### Frontend
- Nuxt 3
- Tailwind CSS
- Pinia (state management)
- TypeScript

## Development Notes

### Windows Development
The frontend is configured to run in **client-side mode** (`ssr: false`) to avoid Windows path issues. This is perfect for development and all features work normally. For production deployment on Linux, SSR can be re-enabled. See `WINDOWS_SETUP.md` for details.

### Hot Reload
Both backend (Django) and frontend (Nuxt) support hot reload during development.

### Database
The SQLite database is located at `backend/db.sqlite3`. To reset:
```bash
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py create_mock_data
```

### Admin Access
Default superuser (if created):
- Username: admin
- Email: admin@example.com
- Password: (set during createsuperuser)

## Project Structure

```
hacktheice/
├── backend/              # Django backend
│   ├── config/          # Django settings
│   ├── users/           # User models
│   ├── benefits/        # Benefits models
│   ├── api/             # REST API
│   └── db.sqlite3       # Database
├── frontend/            # Nuxt 3 frontend
│   ├── app/             # App component
│   ├── pages/           # Page components
│   ├── assets/          # CSS and static files
│   └── nuxt.config.ts   # Nuxt configuration
├── readme.md            # Original requirements
├── IMPLEMENTATION_STATUS.md
├── QUICKSTART.md
└── README_DEV.md       # This file
```

## Troubleshooting

### "Module not found" errors
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
```bash
# Backend (change port)
python manage.py runserver 8001

# Frontend (change port)
npm run dev -- --port 3001
```

### Database errors
```bash
cd backend
rm db.sqlite3
rm -rf */migrations/0*.py
python manage.py makemigrations
python manage.py migrate
python manage.py create_mock_data
```

## Contributing

When adding new features:
1. Backend: Create models → Create serializers → Create views → Add URLs
2. Frontend: Create pages → Create components → Add to routing
3. Test both independently before integration

## Resources

- Django: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Nuxt 3: https://nuxt.com/docs
- Tailwind CSS: https://tailwindcss.com/docs
