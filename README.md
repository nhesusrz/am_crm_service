# AG CRM Service API

# Development Overview

This project uses a modern stack for building and testing a robust backend application. I use _FastAPI_ for fast, asynchronous web API development, with _SQLAlchemy_ for database interactions, and _PostgreSQL_ as the database. File storage is managed with _MinIO_, an _S3-compatible_ storage service. The application is containerized using _Docker_ and managed with _Docker Compose_. For development and testing, I employ _pytest_ for testing with _pytest-cov_ for coverage reports. Code quality tools like _black_ and _isort_ ensure code formatting and organization, while _ruff_ helps with linting. Asynchronous programming is leveraged to handle multiple tasks concurrently, improving performance.

## Installation

- Clone the repo <https://github.com/nhesusrz/am_crm_service.git>

- Install and configure Poetry: <https://python-poetry.org/docs/basic-usage/>
- `cd am_crm_service`
- Activate the virtual environment: `poetry shell`
- Install app dependencies from `pyproject.toml` file: `poetry install`
- Run `uvicorn app.main:app --reload`  to run the application locally.

Navigate to <http://localhost:8000/docs> find documentation and resources to test the application locally.

## Alembic Migrations

### Auto generating migrations

- Run `alembic revision --autogenerate -m "migration message"` to auto generate migrations.
- Run `alembic upgrade head` to apply migrations.
- Run `alembic downgrade -1` to downgrade migrations.
- NOTE: Do not modify the imports from `alembic/env.py` file.

# Project Setup and Usage

## Prerequisites
Before deploying the application, make sure you have Docker and Docker Compose installed.

### Installing Docker

Follow the instructions on the [official Docker website](https://www.docker.com/) to install Docker for your operating system.

### Installing Docker Compose

To install Docker Compose from the official repository:

1. **Download Docker Compose:** Find the latest release version from the [Docker Compose GitHub releases page](https://github.com/docker/compose/releases).
##
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

2. **Apply Executable Permissions:** Make the Docker Compose binary executable.
##
        sudo chmod +x /usr/local/bin/docker-compose

3. **Verify Installation:** Check that Docker Compose is installed correctly. You should see the version of Docker Compose that you installed.
##
        docker compose --version

## Deployment with Docker Compose

1. Clone the repo <https://github.com/nhesusrz/am_crm_service.git>
2. ##
         cd am_crm_service
3. ##
         mv .env.example .env
4. Run Docker Compose to build and start the services. This command will build the Docker images and start the containers for your application, PostgreSQL, and MinIO.:
    ##
        docker-compose up --build

## Access the Application 
The FastAPI application will be available at http://localhost:8000. Use this URL to interact with the API.

## Accessing MinIO WebUI

To view and manage your buckets and their contents, you can access the MinIO WebUI:
Open your web browser and go to http://127.0.0.1:9001.

Log in using the credentials specified in your .env file:
* Access Key: `<your-minio-access-key>`
* Secret Key: `<your-minio-secret-key>`

This interface allows you to view, create, and manage buckets and their contents.

## Troubleshooting

- Container Status: Check the status of your containers: 
    ##
        docker-compose ps
- Logs: To view the logs for debugging, use: 
    ##
        docker-compose logs


## Using Postman

To test the API, you can use Postman. Import the provided Postman collection file into Postman: [Download Postman Collection](https://github.com/user-attachments/files/16822519/AM_CRM_SERVICE.postman_collection.json)

## Cleaning Up Docker Resources

To clean up everything related to the containers, including volumes and images, follow these steps:

1. Stop and remove containers:
    ##
        docker stop app_container minio_container postgres_container  
    ##
        docker rm app_container minio_container postgres_container
2. The volumes defined in your _docker-compose.yml_ file are _postgres_data_ and _minio_data_. To remove these volumes, use: 
    ##
        docker volume rm postgres_data minio_data
3. To remove the images _postgres:latest_ and _minio/minio_ use: 
    ##
        docker rmi postgres:latest minio/minio
