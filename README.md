# Claim Hunter Backend

A robust FastAPI backend for the Claim Hunter application, providing text analysis capabilities, user authentication, and history tracking. This service uses advanced NLP to identify and analyze claims within text.

## 🚀 Features

- **User Authentication**: Secure registration and login using JWT (JSON Web Tokens) and HttpOnly cookies.
- **Claim Analysis**: Submit text to be analyzed for potential claims using Google's Generative AI.
- **History Tracking**: Store and retrieve past analyses for authenticated users.
- **Database Management**: PostgreSQL integration with Alembic for schema migrations.
- **CORS Support**: Configurable Cross-Origin Resource Sharing for frontend integration.
- **Environment Configuration**: Fully configurable via `.env` files.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Authentication**: `python-jose` (JWT), `passlib` (Bcrypt hashing)
- **AI Integration**: [Google Generative AI](https://ai.google.dev/)
- **Validation**: [Pydantic](https://docs.pydantic.dev/)

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.12 or higher
- PostgreSQL installed and running
- A Google Cloud API Key for Generative AI

### Installation Steps

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/rohitkumar91131/claim-hunter-backend-python.git
    cd claim-hunter-backend-python
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**:
    Create a `.env` file in the root directory with the following variables:
    ```ini
    # Database Configuration
    DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<dbname>

    # Security
    SECRET_KEY=your_super_secret_key_here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    
    # CORS (List of allowed origins)
    BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

    # AI Service
    GOOGLE_API_KEY=your_google_api_key

    # App Settings
    ANALYSIS_TIMEOUT=30
    ENABLE_RATE_LIMIT=True
    ```

5.  **Run Database Migrations**:
    Initialize the database schema:
    ```bash
    alembic upgrade head
    ```

6.  **Start the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be accessible at `http://localhost:8000`.

## 📚 API Documentation

Once the server is running, you can access the interactive API docs at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Authentication (`/auth`)
- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Authenticate and receive an HttpOnly cookie.
- `POST /auth/logout`: Log out (clears cookie).
- `GET /auth/me`: Get current authenticated user details.

#### Analysis (`/analyze`)
- `POST /analyze/text`: Submit a text block for claim analysis.
  - **Body**: `{"text": "Text to analyze..."}`
  - **Auth**: Required

#### History (`/history`)
- `GET /history`: List all past analyses for the current user.
- `GET /history/{id}`: Get detailed results for a specific analysis.

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License.
