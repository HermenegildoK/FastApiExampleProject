# Type-driven design example in Python

In his post [Parse, don’t validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/),
Alexis King states that using type-driven design you can improve your code and make sure your input is always what your functions require.

Since Python is not strongly typed, how can we use type-driven design to help us improve our code?
I will show an example where using [Pydantic](https://pydantic-docs.helpmanual.io/) and [FastAPI](https://fastapi.tiangolo.com/) with clean code practices can help us write maintainable, easy to use code.

This is a very simple example.

Do not use in production, if you do not have to. 

# Running app

- crete virtual environment and install dependencies

```shell
pipenv -python 3.8
pipenv install --dev
```

- create `.env` file with content:

```editorconfig
API_PREFIX=/api
USE_DATABASE=False

```

- run app:

```shell
cd web_app_example
uvicorn main:app_setup --port 8002
```

- if you need database update `.env` file:

```editorconfig
API_PREFIX=/api
USE_DATABASE=True
DATABASE_URL=postgresql://USER:PASS@HOST:PORT/DBNAME
LOGGING = 'LOGGING = '{"LOG_PATH": "/var/logs/fastapiexample", "LOG_TO_FILE": true, "LOG_TO_LEVEL_FILES": true, "JSON_LOG_FILE": "api_log.json", "LOG_SQL": true, "LOG_JSON": true, "MIN_LOG_LEVEL": 10}'
'
```
where `DATABASE_URL` is a valid url to PostgreSQL database


## Running tests

```shell
pytest 
```
