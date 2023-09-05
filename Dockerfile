# syntax=docker/dockerfile:1.2
FROM python:3.9-slim
# put you docker configuration here
WORKDIR /challenge

ENV PYTHONPATH=/challenge

COPY ./challenge /challenge
COPY ./challenge/model.py /challenge/challenge/model.py

COPY ./requirements.txt /challenge/requirements.txt 
COPY ./data/data.csv /challenge/data/data.csv

RUN pip install -r requirements.txt 

EXPOSE  8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]