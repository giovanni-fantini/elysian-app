# Example Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only the allowed files and directories
COPY . .

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-dev

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]