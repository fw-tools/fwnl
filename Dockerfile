FROM python:3.8

WORKDIR /usr/src/fwnl
COPY . .

RUN pip install --upgrade pip pipenv
RUN python -m pipenv install -d
RUN python -m pipenv run spacy download en_core_web_md

CMD [ "python", "-m", "pipenv", "run", "fwnl-web" ]
