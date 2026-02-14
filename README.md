# Claim Hunter Backend

A FastAPI backend for text analysis with user authentication and history tracking.

## Features
- **Authentication**: Register, Login, JWT Tokens (OAuth2).
- **Analysis**: Submit text for analysis and receive structured JSON results.
- **History**: View past analyses.
- **Database**: PostgreSQL with Alembic migrations.

## Setup

### Prerequisites
- Python 3.12+
- PostgreSQL
- Virtual Environment (recommended)

### Installation
1.  **Clone the repository** (if not already done).
2.  **Create and activate virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, use the command below)*
    ```bash
    pip install fastapi uvicorn sqlalchemy alembic pydantic-settings python-jose[cryptography] passlib[bcrypt] python-dotenv psycopg2-binary
    ```
4.  **Configure Environment**:
    - Ensure `.env` exists with correct `DATABASE_URL`.
    #### Example .env
    ```ini
    DATABASE_URL=postgresql://claimuser:123456@localhost:5432/claimhunter
    SECRET_KEY=supersecretkey
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

### Database Migration
Run the following to apply database changes:
```bash
alembic upgrade head
```

### Running the Server
Start the development server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
Explore the documentation at `http://localhost:8000/docs`.

## API Usage

### Auth
- **POST /auth/register**: Create a new account.
- **POST /auth/login**: Login to get a Bearer token.
- **GET /auth/me**: Get current user details.

### Analysis
- **POST /analyze**: Submit text for analysis.
    - Headers: `Authorization: Bearer <token>`
    - Body: `{"text": "Sample text to analyze"}`
- **GET /history**: Get list of past analyses.
- **GET /history/{id}**: Get details of a specific analysis.
