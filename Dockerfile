FROM python:3.8-slim-buster



WORKDIR /code
COPY ./app .
RUN mkdir /data
RUN apt-get update \
    && /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt


ENTRYPOINT [ "sh", "killstreamloop.sh" ]