# syntax=docker/dockerfile:1
FROM continuumio/miniconda3
LABEL author="balansrikant@gmail.com"
LABEL version="1.0"

COPY /src/ .
COPY ../HL/ ./HL/
COPY production_environment.yml .
RUN conda env create -f production_environment.yml
RUN conda clean -afy

EXPOSE 80

CMD [ \
  "conda", "run", "-n", "hl-scraper", \
  "python", "-m", "hl-scraper", "/HL/" \
]