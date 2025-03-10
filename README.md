## Installation & Setup

### Backend
1. set up .env
```sh
cd backend/backend
touch .env
```

in `.env` add the variables below. follow [google_cloud_sql_tutorial]https://www.geeksforgeeks.org/setting-up-google-cloud-sql-with-flask/ to set up the `.env`. Talk to Alex if you are having issues.

**DISABLE BILLING ON GOOGLE CLOUD SQL INSTANCE WHEN NOT USING YOU WILL INCUR COSTS!!!**

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
poetry run pytest
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


