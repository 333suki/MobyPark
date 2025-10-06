# How to run server
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
`fastapi dev api/new_server.py`

# How to run tests
## Create & activate venv
See above
## Run tests
`pytest api/tests.py`
