# Live Server
`mobypark.siudowski.com`

Example API call
`mobypark.siudowski.com/auth/register`

# Instructions
## Virtual environment
### Create venv
#### Windows
`python -m venv .venv/`
#### Linux
`python3 -m venv .venv/`
### Activate venv
#### Windows
`.\.venv\Scripts\activate`
#### Linux - Bash
`source .venv/bin/activate`
#### Linux - Fish
`source .venv/bin/activate.fish`
### Install requirements
`pip install -r requirements.txt`

## Running the servers
### Old server
From root directory, run
`python old_api/server.py`
### New server
You can start the server in any of the following ways:
- Directly run the Python file (no extra commands):
  - From project root: `python -m app.main`
- Using uvicorn (previous method):
  - From `app` directory: `uvicorn app.main:app --reload`

## Running tests
### Tests for the old server
`pytest old_api/tests.py`
### Tests for the new server
Run all commands from the root directory.
#### All tests
```bash
pytest
```
Add `-v` flag for more verbose output.

If it complains about module 'app' not found:
```bash
PYTHONPATH=. pytest -v
```
But the `pytest.ini` file should do that automatically.
#### Specific test file
```bash
pytest tests/[filename]
```

## How to create a new database model
- Create a new file in `app/db/models/`, see `user.py` for example.
- Import this file in `app/db/base.py`
- Make a database migration

## Database migrations
- Run these commands in root directory.
  - `alembic -c app/alembic.ini revision --autogenerate -m "message"`, and choose a fitting message.
  - `alembic -c app/alembic.ini upgrade head`

# New server structure
- Root `app` directory
  - `alembic` subdirectory contains configuration for alembic, the database migration tool.
  - `api` subdirectory includes API logic
    - `auth` subdirectory contains endpoints for login, registering.
    - `parking_lots` subdirectory contains endpoints for parking lot management.
    - `parking_sessions` subdirectory contains endpoints for parking session management.
    - `users` subdirectory contains endpoints for listing users (for admins).
  - `core` subdirectory includes some configuration we can use.
  - `db` subdirectory contains database information and models. In the `base.py` file, we include data models to be included in migrations.

## How to call authenticated endpoints (e.g., /vehicles)

After you log in at `/auth/login`, you will receive a JSON response containing a `token`. You must send this token in the `Authorization` header when calling protected endpoints like `/vehicles`.

Header format expected by the server:

- Header name: `Authorization`
- Header value: `Bearer <your_jwt_token_here>`

The backend automatically accepts both raw tokens and the `Bearer` format, but using the `Bearer` prefix is recommended and standard.

### Postman steps
1. Make a POST request to `/auth/login` with your credentials.
2. Copy the `token` value from the response.
3. Create a new request: `GET /vehicles/`.
4. Go to the Headers tab and add:
   - Key: `Authorization`
   - Value: `Bearer <paste-your-token>`
5. Send the request. You should receive your vehicles list.

Alternatively in Postman, you can use the Authorization tab:
- Type: `Bearer Token`
- Token: `<paste-your-token>`

If your token is expired, the server will respond with status 498. In that case, log in again to obtain a fresh token.
