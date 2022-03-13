# syntax=docker/dockerfile:1
#FROM continuumio/miniconda3
FROM python:3.9-slim-buster
LABEL author="balansrikant@gmail.com"
LABEL version="1.0"

COPY app .
#COPY ../app/ ./app/
#COPY production_environment.yml .
#RUN conda env create -f production_environment.yml
#RUN conda clean -afy

RUN pip install flask \
                flask-sqlalchemy \
                pandas \
                lxml \
                gunicorn
#RUN ls
EXPOSE 5000

#CMD [ \
#  "conda", "run", "-n", "hlscraper", \
#  "python", "-m", "run", "--host", "127.0.0.1", "/app/"\
#]

#CMD [ \
#  "python", "-m", "run", "--host", "0.0.0.0"\
#]

CMD [ \
    "gunicorn", "--bind", "0.0.0.0:5000", "run:app"\
]