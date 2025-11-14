# SUPPORT+ Quick Start Guide

## Prerequisites
- Python 3.12+
- Node.js 22+
- npm 10+

## Backend Setup (Django)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Test Data
```bash
# This creates 11 benefits and 9 commercial offers
python manage.py create_mock_data
```

### 4. Create Admin User
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (enter your password)
```

### 5. Start Development Server
```bash
python manage.py runserver
```

The backend will be available at:
- **API:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/

## Frontend Setup (Nuxt 3)

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The frontend will be available at:
- **App:** http://localhost:3000/

## Testing the API

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ivan",
    "email": "ivan@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "beneficiary_category": "pensioner",
    "region": "Республика Саха (Якутия)",
    "phone": "+79991234567"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ivan",
    "password": "testpass123"
  }'
```

Save the `access` token from the response.

### 3. Get Benefits (Authenticated)
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/benefits/
```

### 4. Get Personalized Benefits
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/benefits/?personalized=true"
```

### 5. Get Dashboard Data
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/benefits/dashboard/
```

### 6. Search Benefits
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/benefits/?search=транспорт"
```

### 7. Filter by Type
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://localhost:8000/api/benefits/?type=federal"
```

### 8. Get Commercial Offers
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/offers/
```

## Admin Panel Features

Access http://localhost:8000/admin/ with your superuser credentials.

### What You Can Do:
1. **Users Management**
   - View all registered users
   - Check beneficiary categories
   - Manage verification status

2. **Benefits Management**
   - Create/Edit/Delete benefits
   - Assign categories and regions
   - Set validity dates and status

3. **Commercial Offers**
   - Manage partner offers
   - Set discounts and promo codes
   - Configure target groups

4. **Categories & Regions**
   - Add new benefit categories
   - Manage Russian regions

## Available API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/oauth/gosuslugi/` - Mock Gosuslugi OAuth
- `GET /api/auth/me/` - Get current user info

### Benefits
- `GET /api/benefits/` - List all benefits
- `GET /api/benefits/{id}/` - Get benefit details
- `GET /api/benefits/recommended/` - Get personalized recommendations
- `GET /api/benefits/dashboard/` - Get dashboard summary

**Query Parameters:**
- `?search=keyword` - Search in title, description
- `?type=federal|regional|municipal` - Filter by type
- `?status=active|expiring_soon|expired` - Filter by status
- `?region=RegionName` - Filter by region
- `?category=slug` - Filter by category
- `?personalized=true` - Show only relevant to user
- `?ordering=-created_at` - Sort by field

### Commercial Offers
- `GET /api/offers/` - List all offers
- `GET /api/offers/{id}/` - Get offer details

**Query Parameters:**
- `?search=keyword` - Search
- `?partner_category=category` - Filter by partner type
- `?region=RegionName` - Filter by region
- `?personalized=true` - Show only relevant to user

### User Profile
- `GET /api/profile/` - Get user profile
- `PUT /api/profile/` - Update profile
- `POST /api/profile/hide_benefit/` - Hide a benefit
- `POST /api/profile/unhide_benefit/` - Unhide a benefit

### Data
- `GET /api/categories/` - List categories
- `GET /api/regions/` - List regions

### Export
- `GET /api/export/benefits/pdf/` - Export benefits to PDF

## Sample Data

### Benefits Created (11 total)
- **Federal (6):** Transport, Medicine, Utilities, Social payments, Family support, SVO support
- **Regional (3):** Yakutsk transport, Yakutsk utilities, Yakutsk housing
- **Municipal (2):** Yakutsk social aid, Yakutsk medical services

### Commercial Offers (9 total)
- Pharmacy discounts
- Grocery store offers
- Utility services
- Telecom deals
- Banking services
- Transportation discounts
- Education programs

### Beneficiary Categories
- pensioner (Пенсионер)
- disability_1 (Инвалидность 1 группы)
- disability_2 (Инвалидность 2 группы)
- disability_3 (Инвалидность 3 группы)
- large_family (Многодетная семья)
- veteran (Ветеран)
- low_income (Малоимущий)
- svo_participant (Участник СВО)
- svo_family (Семья участника СВО)

### Regions
- Республика Саха (Якутия) - Code: 14
- Москва - Code: 77
- Санкт-Петербург - Code: 78
- Республика Адыгея - Code: 01
- Московская область - Code: 50

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError`
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

**Problem:** Database errors
```bash
# Solution: Delete and recreate database
rm db.sqlite3
python manage.py migrate
python manage.py create_mock_data
```

**Problem:** CORS errors
```bash
# Solution: Check CORS_ALLOWED_ORIGINS in settings.py
# Make sure frontend URL is included
```

### Frontend Issues

**Problem:** Module not found
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Problem:** Can't connect to API
```bash
# Solution: Check API_BASE_URL in nuxt.config.ts
# Make sure backend is running on localhost:8000
```

## Next Steps

After getting both backend and frontend running:

1. **Test Authentication Flow**
   - Register a new user
   - Login
   - View dashboard

2. **Test Benefit Browsing**
   - View all benefits
   - Filter by category
   - Search for specific benefits
   - View benefit details

3. **Test Personalization**
   - Set beneficiary category in profile
   - View personalized recommendations
   - Hide/unhide benefits

4. **Test Accessibility**
   - Change font size
   - Change color mode
   - Test keyboard navigation
   - Test with screen reader

## Development Tips

### Backend
- Use `python manage.py shell` for interactive Python console
- Use `python manage.py dbshell` for database console
- Run `python manage.py check` to check for issues

### Frontend
- Use Vue DevTools browser extension
- Check browser console for errors
- Use `npm run build` to test production build

## Production Deployment (Future)

When ready to deploy:

1. Set `DEBUG = False` in Django settings
2. Configure proper `SECRET_KEY`
3. Set up proper database (PostgreSQL recommended)
4. Configure nginx/apache as reverse proxy
5. Set up SSL certificates
6. Build frontend: `npm run build`
7. Configure environment variables

## Support & Documentation

- **Django Docs:** https://docs.djangoproject.com/
- **Django REST Framework:** https://www.django-rest-framework.org/
- **Nuxt 3 Docs:** https://nuxt.com/docs
- **Tailwind CSS:** https://tailwindcss.com/docs
