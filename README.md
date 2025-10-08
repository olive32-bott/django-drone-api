#  Drone Delivery API (Django + DRF)

**Tech Stack:** Django · Django REST Framework · SQLite

Prototype REST API for managing drones and tracking the medications they carry.

---

##  Features

-  **Register drones and medications** (with image uploads)
-  **Load medications** onto a drone with rule enforcement:
  - Battery ≥ 25%
  - Drone state must be `LOADING`
  - Total load weight ≤ drone weight limit (≤ 500g)
  - After loading, state automatically becomes `LOADED`
-  **List drones available for loading**
-  **Check battery level** for a specific drone
-  **View medications** loaded on a drone
-  OpenAPI schema + Swagger UI at [`/api/docs/`](http://127.0.0.1:8000/api/docs/)
-  Basic unit tests included

---

## Quickstart

```bash
# 1️ Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2️ Install dependencies
pip install -r requirements.txt

# 3️ Apply migrations
python manage.py migrate

# 4 Run development server
python manage.py runserver
