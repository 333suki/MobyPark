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
`python api/server.py`
## Run new server
`fastapi dev app/main.py`

# How to run tests
## Create & activate venv
See above
## Run tests
`pytest api/tests.py`

# New server structure
- Root `app` directory
  - `core` subdirectory includes some configuration we can use.
  - `api` subdirectory includes API logic
    - `users` subdirectory contains endpoints for listing users (for admins).
    - `auth` subdirectory contains endpoints for login, registering.