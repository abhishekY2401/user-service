# User Microservice

This microservice handles user authentication and profile management. It uses JWT-based authentication to secure access to user data, and communicates with other microservices using message queue.
## 💡 Features

- User registration and Login: Secure Authentication using JWT.
- JWT Authentication: Protects all queries and mutations with token-based authentication.
- User Profile Management: Users can manage their personal information, including contact details and address.
- Event-Driven Architecture: Emits events to RabbitMQ for other microservices like Order or Product to maintain database consistency.

## 🛠️ Technologies Used

- Language: Python
- Framework & Libraries:
    - Flask
    - SQLAlchemy (Database ORM)
    - Pika (RabbitMQ client)
    - Alembic (for Database Migrations)
- Database: PostgreSQL
- Message Queue: RabbitMQ
- GraphQL: Ariadne (for GraphQL implementation)
- Authentication: JWT (JSON Web Tokens)

## 📋 Prerequisites

Before setting up the microservice, ensure the following are installed:
- [Python 3.8+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [RabbitMQ](https://www.cloudamqp.com/)

## ⚙️ Setup Instructions

### 1. Clone the Repository
    
    git clone https://github.com/abhishekY2401/user-service.git
    cd user-service
    

### 2. Install Dependencies
Create a virtual environment and install the required Python dependencies:

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt

### 3. Database Setup
Ensure PostgreSQL is running, and configure the config.py with your database connection details:

    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/user_db'

Run database migrations:

    flask db upgrade

### 4. RabbitMQ Setup
Ensure RabbitMQ is running, and update config.py if necessary:

    RABBITMQ_URL = 'amqp://guest:guest@localhost:5672/'

### 5. Environment Variables
Create a .env file to store your environment variables:

    JWT_SECRET_KEY=your_jwt_secret_key
    POSTGRES_USER=your_postgres_user
    POSTGRES_PASSWORD=your_postgres_password
    POSTGRES_DB=user_db
    RABBITMQ_URL=your_rabbitmq_url

### 6. Running the Microservice
To start the service locally:

    flask run --host='0.0.0.0' --port='8000'

### 7. GraphQL Playground
Once the service is running, access the GraphQL playground at 
    
    http://localhost:8000/graphql

## 🔍 GraphQL API

Mutations:

- Sign Up Register a new user
```
  mutation {
    signUp(username: "johndoe", email: "john@example.com", password: "password123") {
      success
      message
    }
  }
```

- Login Authenticate the user and retrieve a JWT token.
```
  mutation {
  login(username: "johndoe", password: "password123") {
    success
    token
    message
  }
}
```

Queries

Get User Profile (Protected with JWT) Retrieve the profile information of a logged-in user
```
  query {
    getUserProfile {
      id
      username
      email
      address
      contact
    }
  }
```

🔐 JWT Protection
All protected queries and mutations require a valid JWT token. Pass it as a Bearer token in the headers:
```
  Authorization: Bearer <your_jwt_token>
```


## 📡 Event-Driven Architecture

1. ```user.registered```: Emitted when a new user is registered.
This event is consumed by Order microservices to maintain the user-related data.

2. ```user.profile.updated```: Emitted when a user has updated the profile.
This event is consumed by Order microservices to update the user-related data.

To test this event driven architecture, you can follow the same steps for other microservices and run the following command in Order microservice:
```
python consumer.py
```

## 🐇 RabbitMQ Configuration

- Go to [RabbitMQ](https://www.cloudamqp.com/) site and sign up with google.
- Create a new instance and start the instance server.
- Once this is done, you will be directed to dashboard from there copy the URL from AQMP Details Section.
- Ensure RabbitMQ is properly configured with an exchange and queue for event communication.

## 🛠️ Troubleshooting

- PostgreSQL or RabbitMQ not running: Ensure that PostgreSQL and RabbitMQ services are running before starting the microservice.
- Environment Variables: Double-check the .env file for any misconfigurations.
