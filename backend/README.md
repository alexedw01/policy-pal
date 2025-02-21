## Test Cases

**test_app.py**
https://github.com/alexedw01/policy-pal/blob/main/backend/backend/test_app.py
### Unit Tests
1. User Registration - Success [test_register_success]
- **Description:** Test is new user can register successfully
- **Endpoint:** 'POST /register'
- **Expected Outcome:** Returns `201 Created` with the message `"User created successfully"`.

2. User Registration - Missing Fields [test_register_missing_fields]
- **Description:** Tests if registration fails when required fields are missing.
- **Endpoint:** `POST /register`
- **Expected Outcome:** Returns `400 Bad Request` with an error message.

3. User Registration - Duplicate User [test_register_duplicate]
- **Description:** Tests if the system prevents duplicate registrations.
- **Endpoint:** `POST /register`
- **Expected Outcome:** The first registration succeeds (`201`), the second fails (`400`).

### Integration Tests
4. Get Users List [test_get_users]
- **Description:** Tests retrieving a list of registered users.
- **Endpoint:** `GET /users`
- **Expected Outcome:** Initially empty, but contains registered users after registration.

### API Endpoint Tests
5. Login with Email - Success [test_login_success_with_email]
- **Description:** Tests if a registered user can log in using their email.
- **Endpoint:** `POST /login`
- **Expected Outcome:** Returns `200 OK` with `"Logged in successfully"`.

6. Login with Username - Success [test_login_success_with_username]
- **Description:** Tests if a registered user can log in using their username.
- **Endpoint:** `POST /login`
- **Expected Outcome:** Returns `200 OK` with `"Logged in successfully"`.

7. Login - Missing Fields [test_login_missing_fields]
- **Description:** Tests if login fails when required fields are missing.
- **Endpoint:** `POST /login`
- **Expected Outcome:** Returns `400 Bad Request` with an error message.

8. Login - Invalid Credentials [test_login_invalid_credentials]
- **Description:** Tests if login fails with incorrect credentials.
- **Endpoint:** `POST /login`
- **Expected Outcome:** Returns `401 Unauthorized` with an error message.

### CLI Tests
9. Initialize Database [test_init_db_cli]
- **Description:** Tests if the CLI command correctly initializes the database.
- **Command:** `init-db`
- **Expected Outcome:** Prints `"Database tables created."`

10. Reset Database [test_reset_db_cli]
- **Description:** Tests if the CLI command correctly resets the database.
- **Command:** `reset-db`
- **Expected Outcome:** Prints `"Database reset complete."`

## **Running Tests**
To run all tests, use the following command:

```bash
pytest
```

For a specific test, run:

```bash
pytest -k "test_register_success"
