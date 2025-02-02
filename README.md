
# Hold on pushing .gitignore not added yet. need if for private key protection

## Installation & Setup

### Backend
1. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)

Linux/MacOS:
```sh
curl -sSL https://install.python-poetry.org | python3 - 
```

Windows:
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

2\. Install backend dependencies:
```sh
cd backend
poetry install
```

4\. Run the backend:
```sh
poetry run flask run
```

### Frontend
`TODO`

### Database (Google Cloud SQL)
- Ensure PostgreSQL instance is created and update the connection in the backend

