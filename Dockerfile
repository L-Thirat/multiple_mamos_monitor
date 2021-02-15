FROM python:3.5.3

LABEL maintainer="Thirat"\
      name="Thirat"\
      version="1.0"

RUN pip3 --no-cache install --upgrade pip 

WORKDIR /app

ENV FLASK_APP=app_getonly.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY . /app

RUN pip3 --no-cache install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3" ]
CMD [ "app_getonly.py" ]
