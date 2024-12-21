FROM python:3.13.1-slim

WORKDIR /app

# System dependencies required for building some Python packages
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.4.2
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy only the dependency files first for caching
COPY pyproject.toml poetry.lock /app/

# Install dependencies (no dev dependencies if you're building a production image)
RUN poetry install --no-root --no-interaction --no-ansi

# Now copy the source code
COPY auth_module/ /app/auth_module/

# Expose the port if the application runs on 8080
EXPOSE 8080

# Environment variables if needed
ENV ENV=production

# Run the application
# Adjust the command to point to your actual ASGI or WSGI entrypoint
CMD ["poetry", "run", "uvicorn", "lib.controllers.auth_controller:router", "--host", "0.0.0.0", "--port", "8080"]
