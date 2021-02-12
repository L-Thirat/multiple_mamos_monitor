FROM python:3.5.3

LABEL maintainer="Thirat"\
      name="Thirat"\
      version="1.0"

RUN pip3 --no-cache install --upgrade pip 

WORKDIR /app

COPY . /app

RUN pip3 --no-cache install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3" ]
CMD [ "app_getonly.py" ]
