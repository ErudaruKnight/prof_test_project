# Prof Test Project

This Flask application provides a simple system for running career and knowledge tests. The project includes:

- User authentication
- Admin interface for managing tests
- A standalone career orientation test loaded from `docs/career_test_structure.md`
- An EGE calculator

## Setup

Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

## Running

Initialize the database and start the development server:

```bash
python run.py
```

## Testing

Run the unit tests with:

```bash
pytest -q
```
