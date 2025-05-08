# Life App

> A modular personal management app built with Angular and TailwindCSS.
> Currently under active development — this release focuses on list-based modules.

![Dashboard Screenshot](screenshots/dashboard.png)

## ✨ Overview

**Life App** is a personal dashboard for managing modular tools that help organise your digital life.
Version 1.0 introduces foundational support for list-based modules — think of it like simple, flexible todo or checklist modules, with more features planned in future updates.

## 🔧 Features in v1.0

- Modular architecture with support for dynamic modules
- Customisable list modules (e.g., shopping lists, task checklists)
- User authentication with token-based access
- Responsive layout and mobile-friendly design
- Simple, clean interface built with TailwindCSS

![Login Screenshot](screenshots/login.png)

## 🧪 Demo

You can try out the app live at:
🔗 [https://life.domsapps.com](https://life.domsapps.com)

**Sample credentials:**
~~~
Email: demo@demo.com
Password: demo1234
~~~

> Feel free to play around, this account is temporary and reset regularly.

## 🧱 Tech Stack

### Frontend

- **Framework:** Angular v19
- **Styling:** TailwindCSS with PostCSS
- **Icons:** `ng-icons` with Ionicons
- **Routing:** Angular Router with protected routes

### Backend

- **Language:** Python 3.12
- **Framework:** Django + Django REST Framework (DRF)
- **Database:** PostgreSQL
- **Auth:** JWT-based authentication
- **Swagger:** DRF Spectacular
- **Testing:** Django’s built-in test runner with `APITestCase` coverage
- **CORS & Security:** Configured for cross-origin requests and HTTPS deployments

## 📦 Setup Instructions

### 🔹 Backend (`LifeAPI`)

> **Note:** You’ll need a running PostgreSQL database before starting the backend.
> For local development, you can use Docker with the image: `postgres:17.2-alpine`.

~~~
cd Life/LifeAPI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create a database in PostgreSQL
# Set environment variables in a `.env` file (see .env.example for reference)

# Apply migrations and run the server
python3 manage.py migrate
python3 manage.py runserver

~~~

### 🔹 Frontend (`LifeUI`)

~~~
cd Life/LifeUI
npm install
npm start
~~~

Ensure the frontend is pointing to your backend API in `src/environments/environment.ts`.

## 🗺️ Roadmap

- ✅ v1.0 — List Module (basic CRUD)
- 🚧 v1.1 — Budget Module (in development)
- 🔜 Future: Notes, Calendar, Reminders, etc.

## 📷 Screenshots

![List module Configuration Screenshot](screenshots/list-module-configuration.png)

![List module Data Screenshot](screenshots/list-module-data.png)


## 📄 License

MIT License
