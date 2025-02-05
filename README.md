## Authentication Module

### Setup

1.  **Environment Variables:** Create a `.env` file in the root directory and define the following environment variables:

    ```bash
    DATABASE_URL=your_database_url
    JWT_SECRET_KEY=your_jwt_secret_key
    SOCIAL_GOOGLE_CLIENT_ID=your_google_client_id
    SOCIAL_GOOGLE_CLIENT_SECRET=your_google_client_secret
    ```

2.  **Dependencies:** Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Database:** Set up the database by running the migrations:

    ```bash
    alembic upgrade head
    ```

### Testing

1.  **Unit Tests:** Run the unit tests using pytest:

    ```bash
    pytest
    ```

2.  **Integration Tests:** Write integration tests to simulate complete workflows, including social login, token issuance, and user interactions. These tests should interact with the actual database and external APIs.

### Building

1.  **Docker:** Build the Docker image:

    ```bash
    docker-compose build
    ```

2.  **Run:** Run the application using Docker Compose:

    ```bash
    docker-compose up
    ```

### API Endpoints

The following API endpoints are available:

- `/api/auth/register`: Register a new user.
- `/api/auth/login`: Log in a user.
- `/api/auth/refresh`: Refresh an access token.
- `/api/auth/logout`: Log out a user.
- `/api/auth/social-login`: Log in using a social provider.

### Security Considerations

- **Token Management:** Use short-lived access tokens and refresh tokens. Secure tokens with HTTP-only, Secure, and SameSite cookies.
- **Data Protection:** Hash passwords using bcrypt or Argon2. Encrypt sensitive data at rest.
- **Rate Limiting:** Protect endpoints from brute-force attacks using rate-limiting middleware.
- **OAuth State Parameter:** Prevent CSRF attacks in OAuth flows by validating the `state` parameter.
- **Error Feedback:** Avoid detailed error messages that might expose sensitive data.

### Event-Driven Integration

The authentication module publishes events for other modules, such as notifications and analytics. These events include `UserLoggedIn`, `UserRegistered`, and `UserSocialLinked`. Other modules can subscribe to these events to trigger workflows, such as sending welcome emails.
