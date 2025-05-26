# APS Emergy Calculator Service

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) 
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

Backend service for calculating emergy and sustainability indicators based on LCI (Life Cycle Inventory) data.

## Features

- User authentication with JWT
- File upload support for CSV and Excel files
- Integration with external LCI service
- Emergy calculations and sustainability indicators
- RESTful API endpoints
- SQLite database storage
- Comprehensive test coverage

## Requirements

- Python 3.8+
- FastAPI
- SQLModel
- Pandas
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/wellingtonrsantos/aps-emergy-calculator-service.git
cd aps-calculadora-emergia-service
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your configuration.

## Configuration

The following environment variables are required:

- `DATABASE_URL`: SQLite database URL (default: `sqlite:///./users.db`)
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time
- `LCI_SERVICE_API_URL`: External LCI service URL

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

After starting the server, access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:

```bash
pytest
```

To generate a coverage report in HTML format:

```bash
pytest -v --cov=app --cov-report=html
```

This will create a detailed HTML coverage report in the `htmlcov` directory. You can open `htmlcov/index.html` in your browser to view:

- Line-by-line coverage analysis
- Branch coverage 
- Missing lines
- Detailed coverage statistics per module
- Interactive source code view with coverage highlighting

The report helps identify areas of code that need additional test coverage.

## External LCI Service Integration

This project integrates with an external LCI (Life Cycle Inventory) service for retrieving product data and flows. The LCI service implementation can be found at:

[APS LCI Service](https://github.com/wellingtonrsantos/aps-lci-service)

To use endpoints that depend on the external LCI API:

1. Clone and run the LCI service following its README instructions
2. Configure the `LCI_SERVICE_API_URL` in your `.env` file to point to the running LCI service
3. The default URL for local development is `http://localhost:9000/api/lci`

## Project Structure

```
.
├── app/
│   ├── core/          # Core functionality (auth, config, etc.)
│   ├── db/            # Database models and operations
│   ├── exceptions/    # Custom exceptions
│   ├── models/        # Pydantic models
│   ├── routes/        # API endpoints
│   └── service/       # Business logic
├── tests/             # Test cases
├── .env.example       # Environment variables template
├── pytest.ini         # Pytest configuration
└── requirements.txt   # Project dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.