# Policy Pal

Policy Pal is a web application that facilitates legislative voting with a focus on demographic analytics. This document provides the steps to install, set up, and run both the backend and frontend services.

---

## Table of Contents

- [Installation & Setup](#installation--setup)
  - [Backend](#backend)
    - [Environment Setup](#environment-setup)
    - [Dependencies & Running the Server](#dependencies--running-the-server)
    - [Testing](#testing)
  - [Database (Google Cloud SQL)](#database-google-cloud-sql)
  - [Frontend](#frontend)
- [Additional Resources](#additional-resources)

---

## Installation & Setup

### Backend

#### Environment Setup

1. **Configure Environment Variables:**

Navigate to the backend folder and create a `.env` file:

```sh
cd backend/backend
touch .env
```


in `.env` add the variables below. follow [google_cloud_sql_tutorial]https://www.geeksforgeeks.org/setting-up-google-cloud-sql-with-flask/ to set up the `.env`. Talk to Alex if you are having issues.

```sh
PASSWORD =""
PUBLIC_IP_ADDRESS =""
DBNAME =""
DB_USER=""
PROJECT_ID =""
INSTANCE_NAME =""
```
2. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)

Linux/MacOS:
```sh
curl -sSL https://install.python-poetry.org | python3 - 
```

Windows:
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

3. Install backend dependencies:
```sh
cd backend/
poetry install
```

4. Run the backend:
```sh
cd backend/backend
poetry run flask run --port=8080
```

#### Backend Testing
```sh
cd backend/backend
poetry run pytest bills_test.py
poetry run pytest user_test.py
```

### Database (Google Cloud SQL)
- Ensure PostgreSQL instance is created and update the connection in the backend

### Frontend

1. In project directory, run:

```sh
npm install
```
to install all dependencies needed for project.

2. Run

```sh
cd frontend/policypal/
npm run dev
```

to run frontend app. (View in browser at http://localhost:3000)


