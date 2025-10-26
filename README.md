# Habit Tracker API 🚀

A robust Django-based web application for tracking and managing daily habits. Users can create personalized habits, log completions, view progress (e.g., streaks and stats), and receive reminders via a Telegram bot. The API is fully documented with Swagger/Redoc, secured with JWT authentication, and powered by Celery for background tasks like scheduled notifications.

**Project Status**: 100% complete! Includes full CRUD API, Telegram integration, testing with 80%+ coverage, and deployment-ready setup.

## 📋 Features
- **User Authentication**: JWT-based auth via DRF SimpleJWT (login, refresh tokens).
- **Habit Management**: Create, read, update, delete (CRUD) habits with customizable frequencies (daily/weekly/monthly), goals, and descriptions.
- **Progress Tracking**: Log daily completions, view history, calculate streaks, and generate stats (e.g., completion rate).
- **Reminders & Notifications**: Celery tasks with `django-celery-beat` for scheduled habit reminders sent via Telegram bot.
- **Telegram Bot Integration**: Users interact via bot to log habits, get reminders, and query progress (e.g., `/start`, `/log <habit_id>`, `/stats`). Includes a dedicated `telegram_bot` app for handlers and messaging utilities.
- **API Filtering & Search**: Powered by `django-filter` for querying habits by user, frequency, etc.
- **Admin Interface**: Django admin for managing users, habits, and completions.
- **Documentation**: Interactive Swagger UI and Redoc for testing all endpoints.
- **Testing**: Comprehensive unit/integration tests with pytest and coverage reporting.
- **CORS Support**: Ready for frontend integration (e.g., React/Vue app).
- **Database**: PostgreSQL (with SQLite fallback for dev).

## 🛠️ Tech Stack
- **Backend**: Django 5.2.7, Django REST Framework (DRF) 3.16.1
- **Authentication**: djangorestframework-simplejwt 5.5.1
- **Database**: PostgreSQL (psycopg2-binary 2.9.11); SQLite for local dev
- **API Docs**: drf-yasg 1.21.11 (Swagger/Redoc)
- **Async Tasks**: Celery 5.5.3 with Redis 6.4.0 broker; django-celery-beat 2.8.1 for scheduling
- **Bot**: python-telegram-bot 22.5
- **Testing**: pytest 8.4.2, coverage 7.11.0
- **Other**: django-cors-headers 4.9.0, django-filter 25.2, python-dotenv 1.1.1, PyYAML 6.0.3
- **Python**: 3.10+ (with virtualenv)

See [requirements.txt](requirements.txt) for the full list.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip and virtualenv
- PostgreSQL (for production; install via Homebrew on macOS: `brew install postgresql`, or use Docker)
- Redis (for Celery; `brew install redis` on macOS)
- Telegram Bot Token (create one at [@BotFather](https://t.me/botfather) on Telegram)

### Installation
1. **Clone the Repo**:
git clone <your-repo-url>
cd habit_tracker


2. **Set Up Virtual Environment**:
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
pip install --upgrade pip


3. **Install Dependencies**:
pip install -r requirements.txt


4. **Environment Setup**:
- Copy `.env.example` to `.env` (create if needed) and configure:
  ```
  SECRET_KEY=your-django-secret-key
  DEBUG=True  # Set to False in production
  DATABASE_URL=postgresql://user:pass@localhost/habit_tracker  # Or use SQLite: sqlite:///db.sqlite3
  REDIS_URL=redis://localhost:6379/0
  TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
  ALLOWED_HOSTS=localhost,127.0.0.1  # Add your domain in prod
  CORS_ALLOWED_ORIGINS=http://localhost:3000  # For frontend
  ```
- Load env vars: The project uses `python-dotenv` in `settings.py`.

5. **Database Setup**:
python manage.py makemigrations
python manage.py migrate


6. **Create Superuser**:
python manage.py createsuperuser


7. **Run Celery Worker & Beat** (in separate terminals):
Worker (for tasks)
celery -A habit_tracker worker -l info

Beat (for scheduled reminders)
celery -A habit_tracker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler


8. **Set Up Telegram Bot**:
- Add your bot token to `.env`.
- Run the bot handler (if separate): `python telegram_bot/bot.py` (or it's integrated via views/webhooks).
- Set webhook if needed: Use `/setwebhook` endpoint or BotFather.

### Running the Project
1. **Start the Development Server**:
python manage.py runserver

- Access at `http://127.0.0.1:8000/`.

2. **Admin Panel**:
- `http://127.0.0.1:8000/admin/` – Log in to manage habits/users.

3. **API Documentation & Testing**:
- Swagger UI: `http://127.0.0.1:8000/swagger/` (interactive testing with auth).
- Redoc: `http://127.0.0.1:8000/redoc/` (static docs).
- Authenticate via `/api/token/` (POST with username/password) to get JWT tokens.

4. **Run Tests**:
pytest # Or: pytest --cov=habits --cov-report=html

- Coverage report: Open `htmlcov/index.html` in your browser.

5. **Interact with Telegram Bot**:
- Message your bot on Telegram (e.g., `/start` to register, `/habits` to list, `/complete <habit_name>` to log).

## 📖 API Endpoints
All endpoints are under `/api/v1/` (prefixed in `urls.py`). Use JWT tokens in `Authorization: Bearer <token>` header. Full schema in Swagger!

### Authentication
- `POST /api/token/` – Login (body: `{"username": "...", "password": "..."}`) → Returns access/refresh tokens.
- `POST /api/token/refresh/` – Refresh token.
- `POST /api/token/verify/` – Verify token.

### Habits (Requires Auth)
- `GET /api/habits/` – List user's habits (query params: `?frequency=daily&is_active=true` via django-filter).
- `POST /api/habits/` – Create habit (body: `{"name": "Drink water", "frequency": "daily", "goal": 8}`).
- `GET /api/habits/{id}/` – Retrieve habit details.
- `PUT /api/habits/{id}/` – Update habit.
- `DELETE /api/habits/{id}/` – Delete habit.
- `GET /api/habits/{id}/stats/` – Get progress stats (e.g., streak, completion rate).

### Completions (Requires Auth)
- `POST /api/habits/{id}/complete/` – Log completion (body: `{"notes": "Felt great!"}`; auto-adds date).
- `GET /api/habits/{id}/completions/` – List completions for a habit (query: `?date=2023-10-01`).

### Bot/Webhooks (Public for Telegram)
- `POST /api/telegram/webhook/` – Handle bot updates (e.g., user messages for logging).

Example cURL (with auth):
curl -X POST http://127.0.0.1:8000/api/habits/
-H "Authorization: Bearer <your-jwt-token>"
-H "Content-Type: application/json"
-d '{"name": "Exercise", "frequency": "daily", "goal": 1}'


## 🗺️ Project Structure
habit_tracker/
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── .flake8 # Flake8 config (max-line-length=120)
├── habit_tracker/
│ ├── init.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── habits/
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py # Habit, HabitCompletion, User (with telegram_chat_id)
│ ├── serializers.py # DRF serializers
│ ├── views.py # API views (APIViewSets)
│ ├── urls.py # App URLs
│ └── tasks.py # Celery tasks (e.g., send_daily_habits_reminders)
├── telegram_bot/
│ ├── init.py
│ ├── apps.py
│ ├── bot.py # Telegram utilities (e.g., send_telegram_message)
│ ├── views.py # Webhook views for bot updates (if using)
│ └── urls.py # Bot-related URLs
├── tests/ # Pytest files (test_models.py, test_views.py, etc.)
└── README.md


## 🧪 Testing & Quality
- Run `pytest` for all tests (models, views, Celery tasks, bot handlers).
- Coverage: Aim for 80%+; generate report with `pytest --cov`.
- Linting: Use Flake8 (`flake8 .`) with config in `.flake8` (max-line-length=120). Install if needed: `pip install flake8`.

## 🌐 Deployment
1. **Platform**: Heroku, Railway, or DigitalOcean (use PostgreSQL add-on).
2. **Steps**:
   - Push to Git: `git push heroku main`.
   - Set env vars: `heroku config:set TELEGRAM_BOT_TOKEN=... SECRET_KEY=...`.
   - Run migrations: `heroku run python manage.py migrate`.
   - Scale Celery: Use Procfile with `web: gunicorn habit_tracker.wsgi`, `worker: celery -A habit_tracker worker`, `beat: celery -A habit_tracker beat`.
3. **Webhook for Bot**: Set Telegram webhook to your deployed URL: `https://yourapp.com/api/telegram/webhook/`.
4. **HTTPS**: Enforced in production; use Let's Encrypt.

For production DB: Update `DATABASES` in `settings.py` to use PostgreSQL.

## 🤝 Contributing
1. Fork the repo and create a feature branch (`git checkout -b feature/new-endpoint`).
2. Commit changes (`git commit -m "Add habit stats endpoint"`).
3. Run tests (`pytest`) and linting (`flake8 .`).
4. Push and open a PR.

Follow PEP 8. Pull requests welcome!

## 📄 License
MIT License – see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments
- Built with Django, inspired by habit-tracking apps like Habitica.
- Thanks to OpenAI's GPT-4 for development guidance! 🌟

Questions? Open an issue or DM. Start tracking those habits today! 💪 
