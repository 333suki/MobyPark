# Create and activate venv
## Create venv
`python -m venv .venv/`
## Activate venv
### Windows
`.\.venv\Scripts\activate`
### Linux
`source .venv/bin/activate`
## Install requirements
`pip install -r requirements.txt`
## Run old server
`python old_api/server.py`
## Run new server
Be `/app` directory, then run

`uvicorn main:app --reload`

# How to run tests
## Create & activate venv
See above
## Run tests
`pytest api/tests.py`

# How to do database migrations
- After creating new model in `db/models/`, see `user.py` for example.
- Run these commands in `app` directory.
  - `alembic revision --autogenerate -m "init"`, and choose a good name instead of init.
  - `alembic upgrade head`

# New server structure
- Root `app` directory
  - `core` subdirectory includes some configuration we can use.
  - `api` subdirectory includes API logic
    - `users` subdirectory contains endpoints for listing users (for admins).
    - `auth` subdirectory contains endpoints for login, registering.