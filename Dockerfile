FROM python:3.10-slim as python-base

# Set work directory
WORKDIR /uaissistant

# Install system dependencies required for psycopg2 compilation
RUN apt-get update && apt-get install -y \
  libpq-dev \
  gcc \
  # Add any other dependencies your project may need
  && rm -rf /var/lib/apt/lists/*


# Install Poetry
RUN pip3 install poetry && \
  poetry config virtualenvs.create false

# Copy only the dependencies installation files
COPY pyproject.toml poetry.lock* /uaissistant/

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application
COPY ./uaissistant /uaissistant/uaissistant

# Create a non-root user
RUN useradd --create-home appuser
USER appuser
