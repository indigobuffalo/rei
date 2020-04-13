FROM python:3.7.7-slim-buster

COPY . /dashboard
WORKDIR /dashboard

# clean workspace
RUN rm -rf build/ dist/ *.egg-info

# install dependencies
RUN apt-get update && \ 
    apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install pipenv

# setup environment
RUN pipenv update --dev
#   pipenv check  ( broken per: https://github.com/pypa/pipenv/issues/4188 )

# default port for Flask
EXPOSE 5000

ENTRYPOINT pipenv run flask run --host=0.0.0.0

