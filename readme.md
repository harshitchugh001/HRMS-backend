# HRMS Backend API

HRMS Backend is built using FastAPI and provides REST APIs for managing attendance, employees, and weekly analytics.

---

## Live API

- Swagger Docs: https://hrms-backend-lj2z.onrender.com/docs#/
- Base URL: https://hrms-backend-lj2z.onrender.com

---

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn
- Render (Deployment)

---

## Project Structure

```
backend/
│
├── app/
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   ├── database.py
│
├── requirements.txt
└── main.py
```

---

## Setup Locally

### 1. Clone Repo

```bash
git clone <your-repo-url>
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Server

```bash
uvicorn main:app --reload
```

Open: http://127.0.0.1:8000/docs

---

## Key APIs

### Weekly Attendance

**GET** `/attendance/weekly`

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "date": "2026-02-19",
      "day": "Thu",
      "total": 3,
      "present": 2,
      "pct": 67
    }
  ]
}
```

---

## Deployment

Deployed on Render.

Production URL: https://hrms-backend-lj2z.onrender.com

---

## Demo Video

https://www.awesomescreenshot.com/video/49601085?key=bc4923ab9554e7f94a1be1242177df48