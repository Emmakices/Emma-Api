# SQL Server Data API Platform

## FastAPI - Docker - SQL Server - Enterprise-ready

This project is a containerized REST API built with FastAPI that exposes data from multiple SQL Server databases and schemas in a secure, consistent way. It is designed for analytics teams, frontend applications, integrations, and internal services that need a stable HTTP layer over SQL Server.

## Overview

This API provides a reusable framework for exposing SQL Server data via HTTP endpoints. It replaces direct database access with a controlled data access layer that supports:

- Authentication
- Rate limiting
- Pagination
- Filtering
- Dockerized deployment

It can be used to expose:

- E-commerce data
- Finance data
- HR data
- Logs and events
- Geospaital
- Any SQL Server schema or view

## Key Features

- FastAPI with OpenAPI and Swagger documentation
- Dockerized for portability across environments
- SQL Server backend (local VM, on-prem, or cloud)
- API key authentication
- Rate limiting per IP
- Pagination and filtering
- Health check endpoint
- Environment-based configuration
- Support for multiple databases and datasets

## Architecture

### High-level flow

Client (Swagger UI / Frontend / BI Tool)
  |
  v
FastAPI Service (Docker)
  |
  v
Auth and Rate Limit Middleware
  |
  v
SQLAlchemy + ODBC Driver
  |
  v
SQL Server (one or many databases)

This pattern allows teams to consume data without direct database credentials.

## Project Structure

api-platform/
  main.py            # FastAPI application
  Dockerfile         # Container definition
  requirements.txt   # Python dependencies
  .env.example       # Environment variable template
  README.md          # Documentation

## Environment Configuration

Create a .env file based on .env.example.

### SQL Server connection

SQLSERVER_HOST=host.docker.internal
SQLSERVER_PORT=1433
SQLSERVER_DB=YourDatabaseName
SQLSERVER_USER=api_reader
SQLSERVER_PASSWORD=StrongPassword!
SQLSERVER_DRIVER=ODBC Driver 18 for SQL Server

### API security

API_KEY=change_this_key

Credentials are injected at runtime. Do not commit .env files to version control.

## Running the API with Docker

1) Build the image

docker build -t sqlserver-api:1.0 .

2) Run the container

docker run -d \
  --name sqlserver-api \
  --env-file .env \
  -p 8000:8000 \
  sqlserver-api:1.0

3) Access Swagger UI

http://localhost:8000/docs

## Authentication

All protected endpoints require an API key.

### Header

X-API-KEY: <your_api_key>

Authentication is enforced at the API layer to prevent unauthorized access to database resources.

## Example Endpoints

### Health Check
GET /health

### Dataset Access (example)
GET /datasets/{dataset_name}

#### Supports

- Pagination
- Optional date filters
- Controlled exposure via database views

#### Example request

GET /datasets/ecom_events?page=1&page_size=100

## Design Principles

### Why this API exists

- Avoid direct DB access for consumers
- Enforce security and auditing
- Standardize data access
- Decouple applications from database structure

### Why Docker

- Consistent runtime across environments
- Faster onboarding for new teams
- Production-ready deployment model
- Cloud-native compatibility

### Why SQL views (recommended)

- Stable API contracts
- Ability to change underlying tables safely
- Fine-grained permission control

## Security Considerations

- API key authentication
- Read-only DB users recommended
- Rate limiting enabled
- No credentials stored in code
- Can be extended to OAuth or JWT if required

## Scalability and Extensions

This API is designed to grow:

- Add new databases via configuration
- Add new endpoints per dataset
- Add caching (Redis)
- Add metrics (/metrics)

### Deploy to

- Azure App Service
- AWS ECS / Fargate
- Google Cloud Run

## Troubleshooting

### ODBC driver not found
- Ensure the Docker image installs the correct SQL Server driver
- Match driver version in .env

### Login failed
- Ensure SQL Server is in mixed authentication mode
- Ensure DB user exists and has permissions

### Connection refused
- TCP/IP enabled on SQL Server
- Port 1433 open in firewall
- Correct host used (host.docker.internal for local)

## Intended Users

- Data engineering teams
- Backend developers
- Analytics and BI teams
- Internal platform teams
- Integration services

## Author

Built as an enterprise-ready data access layer by Emmanuel Ihetu.
