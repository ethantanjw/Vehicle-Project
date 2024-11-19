# Vehicle Management Service

This repository contains a Python [Flask](https://flask.palletsprojects.com/en/stable/) web app that interacts with a [PostgreSQL](https://www.postgresql.org/) database using a REST API framework. This repository can be used as a Vehicle Management Service. 

# Build and run locally

```
pip install virtualenv
```

```
virtualenv .app                    # Create a virtual environment (do this just once in the directory)
```

```
source .app/bin/activate           # Start virtual environment (do this every time you use a new terminal tab in this directory)
```

## Installing Dependencies
```
pip install -r requirements.txt    # Do this just once. It will install `flask` and `pytest`
```

## Run the Vehicle Management Service locally

```
python app.py                          # Starts a web server on http://127.0.0.1:5000
```

## Run tests locally
```
pytest tests/test_routes.py                            # You should see the tests in test_routes.py run and pass successfully
```

Navigate to [http://127.0.0.1:5000/] and you should see a JSON response providing a list of the API routes.

The `/api` directory contains the API routes `/db` and the contains the Database component.
