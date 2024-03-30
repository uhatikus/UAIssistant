FROM python:3.10-slim as python-base

# Set work directory
WORKDIR /uaissistant

# Install Poetry
RUN pip3 install poetry && \
  poetry config virtualenvs.create false

# Copy only the dependencies installation files
COPY pyproject.toml poetry.lock* /uaissistant/

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Create a non-root user
RUN useradd --create-home appuser
USER appuser

CMD ["python", "-m", "uvicorn", "assistant.main:app", "--host", "0.0.0.0", "--port", "80"]
