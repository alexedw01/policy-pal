# Policy Pal

## Overview
Policy Pal is a web application that tracks and displays congressional bills using the Congress.gov API. Users can browse bills, search by keywords, and upvote bills they find important. The application features AI-generated summaries of bills and real-time updates.

## Features
- Browse latest congressional bills
- Search bills by keywords
- Filter bills by chamber (House/Senate)
- Sort by newest, oldest, or most upvoted
- View detailed bill information with AI summaries
- User authentication system
- Upvoting system for bills

## Project Structure

### Backend (Flask)
- Python Flask application
- MongoDB database
- Congress.gov API integration
- JWT authentication
- RESTful API endpoints

### Frontend (Next.js)
- Next.js 13+ with App Router
- TypeScript
- Tailwind CSS
- User context for authentication
- Responsive design

## Setup Instructions

### Backend Setup
```bash
# Navigate to backend directory
cd policy-pal-backend

# Install poetry if not installed
brew install poetry

# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your MongoDB and Congress.gov API credentials

# Run the development server
poetry run flask run
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend/policypal

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Run the development server
npm run dev
```

## Environment Variables

### Backend (.env)
```plaintext
MONGODB_URI=
CONGRESS_API_KEY=your_congress_gov_api_key
JWT_SECRET_KEY=your_jwt_secret
```

### Frontend (.env.local)
```plaintext
NEXT_PUBLIC_API_URL=
```

## API Endpoints

### Bills
- `GET /api/bills` - Get latest bills
- `GET /api/bills/trending` - Get trending bills
- `GET /api/bills/{id}/full` - Get full bill details
- `POST /api/bills/{id}/upvote` - Upvote a bill

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

## Development

### Running Tests
```bash
# Backend tests
cd policy-pal-backend
poetry run pytest

# Frontend tests
cd frontend/policypal
npm test
```

### Code Style
- Backend follows PEP 8 guidelines
- Frontend uses ESLint and Prettier

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License
MIT License - see LICENSE file for details