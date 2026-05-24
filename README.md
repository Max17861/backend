# 🛒 Full-Stack E-Shop Platform

Welcome to the E-Shop repository! This project is split into a Django REST Framework backend and a React (Vite) frontend.

---

## 🚀 How to Start the Project

You can spin up the entire ecosystem using **Docker** (recommended) or by running the services **natively** on your machine.

### Method 1: Using Docker (Recommended)
Docker automatically handles dependencies, database configuration, and container orchestration in the correct order.

1. Open your terminal at the root of this project.
2. Build and launch the containers with a fresh cache:

   docker compose build --no-cache && docker compose up

### Method 2: Running Natively (Manual Setup)
If running without Docker, you must start the backend first so the frontend has an active API server to connect to.

Step 1: Start the Backend Service

1. Navigate to the backend directory: cd backend

2. Set up your virtual environment and install dependencies (see Backend Guide).

3. Apply database migrations:
    python manage.py migrate
    python manage.py runserver

Step 2: Start the Frontend Client

1. Open a new terminal tab/window and return to the root, then navigate to the frontend: cd frontend

2. Install the required Node packages:
    npm install
    npm run dev 