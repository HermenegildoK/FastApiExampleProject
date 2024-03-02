
# pull the official docker image
FROM python:3.10

RUN addgroup --system app && adduser --system --group app

# set work directory
WORKDIR /simple_example

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get install libpq5
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . .

ENV PYTHONPATH=/simple_example
RUN chown -R app:app $HOME
RUN chown -R app:app /simple_example
USER app
