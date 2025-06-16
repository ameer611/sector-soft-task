# Shop Bot Project

This is a Django project featuring a Telegram bot for a shop/catalog system, complete with a user registration flow, product browsing, shopping cart, and order management. It also includes a Django REST API with Swagger documentation.

---

## Features

- User registration via Telegram (with language and phone number)
- Product category browsing
- Cart and order management via Telegram
- Django REST Framework API (with Swagger UI)
- Dockerized setup for development and production

---

## Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- Telegram Bot Token ([How to get one?](https://core.telegram.org/bots#botfather))

---

## Quick Start

1. **Configure environment variables**

   Set your secrets in `.env` and docker-compose.yml files:

   ```bash
   # Edit .env and set TELEGRAM_BOT_TOKEN, DJANGO_SECRET_KEY, etc.
   ```

2. **Build and start the project**

   ```bash
   docker-compose up --build
   ```

   This will:
   - Start a Postgres database
   - Apply Django migrations
   - Start the Django web server (API and admin)
   - Start the Telegram bot

4. **Create a superuser (for Django Admin)**

   In a new terminal:

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the services**

   - **Django Admin:** [http://localhost:8000/admin/](http://localhost:8000/admin/)
   - **Swagger UI:** [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
   - **Redoc:** [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

6. **Start chatting with your bot on Telegram**

   - Find your bot using the username you set with BotFather and start chatting!

---

## Project Structure

```
shop-bot/
├── bot/                # Telegram bot handlers
├── shop/               # Django app for shop models and API
├── sector_soft_task/   # Django project settings
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Useful Commands

- **Run migrations:**  
  `docker-compose run --rm web python manage.py migrate`
- **Create superuser:**  
  `docker-compose exec web python manage.py createsuperuser`
- **View logs:**  
  `docker-compose logs -f`

---

## API Documentation

After the project is running, visit:

- [Swagger UI](http://localhost:8000/swagger/)
- [Redoc](http://localhost:8000/redoc/)

---

## Environment Variables

See `.env` for all required variables.

---

## Troubleshooting

- **Database errors ("relation ... does not exist"):**  
  Make sure migrations ran successfully. Try:
  ```bash
  docker-compose run --rm web python manage.py migrate
  ```
- **Bot not responding:**  
  Check logs with `docker-compose logs -f bot`. Make sure your `TELEGRAM_BOT_TOKEN` is correct.

---

## License

MIT