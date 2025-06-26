# Subjex

QA Y2 Software Agile Project
Authored: Bradley W
Date: 27 . 06 . 2025

## Perquisites

- You will need node (v20.17.0 (min)) installed on your system.
- You will need python (v3.10.12 (min)) installed on your system.
- You will need venv (a python package for handling virtual environments) installed on your system.

Run in the root directory ```python -m venv venv``` (you may need to use python3 instead of just python)

### On Mac & Linux

Run in the root directory ```source venv/bin/activate```

### On Windows

Run in the root directory ```venv\Scripts\activate```

## Install Dependencies

Run in the root directory ```pip install -r requirements.txt```
Run in the /frontend directory ```npm install```

## Environment Secrets

Utilise the .env.example as a template to create a .env file in the root directory.
You should also create one in the /frontend directory using the .env.template file there. Avoid changing default values given to you, these aren't secret/unique.

## Build

Run in the /frontend directory ```npm run build```

This will create a /out file in the /frontend directory that the flask container references to deliver it's static HTML/JS content. It is not required if you only wish to test/develop the API. It's not a very pleasant developer experience to have to rebuild every time you wish to see any frontend changes in the web application, so see point on hot reload below if you wish to develop the frontend/UI.

## Hot Reload / Developer frontend environment

The current branch is configured to serve a built version of the application from the address served via flask. To get hot reload functionality simply run from the /frontend directory  ```npm run dev```. This will create a frontend server separate from the flask API for you to develop in. You will need to run the flask server at the same time.

## Running the Flask in dev

Run in the root directory ```export FLASK_APP=app.py && flask run``` for subsequent re-running within that terminal you only have to do ```flask run```.

## Running the Flask in prod

Run in the root directory ```gunicorn app:app```. It's worth noting you should modify the .env variable "FLASK_ENV" to be "production" instead of "development".
