FROM python:3.10-slim
WORKDIR /app

# Install poetry
RUN pip install poetry

WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create virtual environment (since we're in container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the source code
COPY src/ src/

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Start the FastAPI application using uvicorn server:
# - main:app: refers to the FastAPI instance in main.py
# - --host 0.0.0.0: allows connections from any IP
# - --port 8080: runs the server on port 8080
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]
