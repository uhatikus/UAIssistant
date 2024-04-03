# Load environment variables from env file
include .env
export

# Define targets and their recipes
.PHONY: onboarding clean install update run

db:
	# Pull the postgres Docker image
	docker pull postgres
	# Create a Docker volume for storing PostgreSQL data
	docker volume create $(VOLUME_NAME)
	# Run a PostgreSQL container
	docker run --name $(CONTAINER_NAME) -e POSTGRES_PASSWORD=$(DB_PASSWORD) -d -p $(DB_PORT):$(DB_PORT) -v $(VOLUME_NAME):/var/lib/postgresql/data postgres
	# Copy the SQL script into the PostgreSQL container
	docker cp $(SQL_SCRIPT) $(CONTAINER_NAME):/init.sql
	# Execute commands in the PostgreSQL container
	docker exec -it $(CONTAINER_NAME) bash -c "psql -U postgres -d postgres -f /init.sql"

clean:
	# Cleanup
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

install:
	@poetry install

update:
	@poetry update

run:
	@poetry run uvicorn uaissistant.main:app --host 0.0.0.0 --port 8000 --reload
