# Stage 1: Build the base with Poetry installed
FROM python:3.12-slim as poetry-base
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app


# Stage 2: Install production dependencies
FROM poetry-base as builder
COPY pyproject.toml poetry.lock ./
# Install only production dependencies
RUN poetry install --no-dev --no-root
# The --no-root flag prevents installing the project itself, which we'll copy later.


# Stage 3: Final production image
FROM python:3.12-slim as production
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy the virtual environment with dependencies from the builder stage
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
# Copy the application source code
COPY src/ ./src/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Use --host 0.0.0.0 to make it accessible from outside the container
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
