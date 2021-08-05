# syntax=docker/dockerfile:1

FROM python:latest

WORKDIR /Docker

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "biopharm.py"]

ENTRYPOINT [ "python3" ]