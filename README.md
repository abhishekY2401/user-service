# User Microservice

This microservice is responsible for managing user authentication and profile information, including JWT-based authentication for secure access.

## Features

- User registration and login.
- JWT-based authentication for secured access to other resources.
- User profile management (name, contact details, address, etc.).
- Events like "User Registered" emitted to RabbitMQ for communication with other microservices.

## Technologies Used

- Language: Python
- Framework: Flask
- Database: PostgreSQL
- Message Queue: RabbitMQ
- GraphQL: Ariadne for GraphQL implementation
- Authentication: JWT (JSON Web Tokens)
- Containerization: Docker
