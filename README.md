# How to run server
## Create venv
`python -m venv .venv/`
## Activate venv
### Windows
`.\.venv\Scripts\activate.bat`
### Linux
`source .venv/bin/activate`
## Install requirements
`pip install -r requirements.txt`
## Run server
`python api/server.py`

# How to run tests
## Create & activate venv
See above
## Run tests
`pytest api/tests.py`
